import torch


class BluesteinDFT:
    # Due to the error in periodic expansion, it can be treated by making up for zeros in the future
    # Now only the central region is relatively accurate, and the surrounding area is affected by pseudo-diffraction by periodic conditions
    def __init__(self, f1, f2, fs, mout, m_input, device="cpu"):
        self.device = torch.device(device)
        self.f1 = f1
        self.f2 = f2
        self.fs = fs
        self.mout = mout
        self.m_input = m_input

        # Frequency adjustment
        f11 = f1 + (mout * fs + f2 - f1) / (2 * mout)
        f22 = f2 + (mout * fs + f2 - f1) / (2 * mout)
        self.f11 = f11
        self.f22 = f22

        # Chirp parameters
        a = torch.exp(1j * 2 * torch.pi * torch.tensor(f11 / fs))
        w = torch.exp(-1j * 2 * torch.pi * torch.tensor(f22 - f11) / (mout * fs))
        self.a = a.to(self.device)
        self.w = w.to(self.device)

        h = torch.arange(
            -m_input + 1,
            max(mout - 1, m_input - 1) + 1,
            device=self.device,
            dtype=torch.float64,
        )
        h = self.w ** ((h**2) / 2)

        self.h = h
        self.mp = m_input + mout - 1
        padded_len = 2 ** int(torch.ceil(torch.log2(torch.tensor(self.mp))))
        self.padded_len = padded_len

        h_inv = torch.zeros(padded_len, dtype=torch.complex64, device=self.device)
        h_inv[: self.mp] = 1 / h[: self.mp]
        self.ft = torch.fft.fft(h_inv)

        b_exp = torch.arange(0, m_input, device=self.device)
        self.b_phase = (self.a**-b_exp) * h[m_input - 1 : 2 * m_input - 1]

        l = torch.linspace(0, mout - 1, mout, device=self.device)
        l = l / mout * (f22 - f11) + f11
        Mshift = -m_input / 2
        self.Mshift = torch.exp(-1j * 2 * torch.pi * l * (Mshift + 0.5) / fs)

    def transform(self, x, dim=-1):
        x = x.to(self.device)
        m = self.m_input

        dim = dim if dim >= 0 else x.ndim + dim

        if x.shape[dim] != m:
            print(m)
            print(x.shape)
            raise ValueError(
                f"Expected dimension {dim} to be of size {m}, but got {x.shape[dim]}"
            )

        x = x.transpose(dim, -1)

        b_phase = self.b_phase.view((1,) * (x.ndim - 1) + (-1,))
        x_weighted = x * b_phase

        original_shape = x_weighted.shape
        x_weighted = x_weighted.reshape(-1, m)

        b_padded = torch.zeros(
            (x_weighted.shape[0], self.padded_len),
            dtype=torch.complex64,
            device=self.device,
        )
        b_padded[:, :m] = x_weighted

        b_fft = torch.fft.fft(b_padded, dim=1)
        conv = b_fft * self.ft[None, :]
        result = torch.fft.ifft(conv, dim=1)

        result = (
            result[:, self.m_input - 1 : self.mp] * self.h[self.m_input - 1 : self.mp]
        )
        result = result * self.Mshift[None, :]

        new_shape = list(original_shape[:-1]) + [self.mout]
        result = result.reshape(*new_shape)

        result = result.transpose(-1, dim)

        return result


class DebyeWolf:
    def __init__(
        self,
        Min,
        xrange,
        yrange,
        zrange,
        Mout,
        lams,  # list of wavelengths
        NA,
        focal_length,
        n1=1,
        device="cpu",
    ):
        self.device = device
        self.Min = Min
        self.xrange = xrange
        self.yrange = yrange
        self.z_arr = torch.linspace(zrange[0], zrange[1], Mout[2], device=device)
        self.Moutx, self.Mouty = Mout[0], Mout[1]
        lams = torch.tensor(lams, device=device)
        self.lams, self.k0, self.n1, self.NA, self.focal_length = (
            lams,
            2 * torch.pi / lams,
            n1,
            NA,
            focal_length,
        )

        self.N = (Min - 1) / 2

        m = torch.linspace(-Min / 2, Min / 2, Min, device=self.device)
        n = torch.linspace(-Min / 2, Min / 2, Min, device=self.device)
        self.m_grid, self.n_grid = torch.meshgrid(m, n, indexing="ij")

        self.th = torch.asin(
            torch.clamp(
                NA * torch.sqrt(self.m_grid**2 + self.n_grid**2) / (self.N * n1), max=1
            )
        )
        self.mask = self.th > torch.arcsin(torch.tensor(NA / n1))
        self.phi = torch.atan2(self.n_grid, self.m_grid)
        self.phi[self.phi < 0] += 2 * torch.pi

        self._sqrt_costh = 1 / torch.sqrt(torch.cos(self.th).unsqueeze(-1))
        self._sqrt_costh[torch.isnan(self._sqrt_costh)] = 0
        self._sqrt_costh[self.mask] = 0

        fs = lams * (Min - 1) / (2 * NA)
        self.fs = fs
        self.bluesteins_y = []
        self.bluesteins_x = []
        self.C = (
            -1j
            * torch.exp(1j * self.k0 * n1 * focal_length)
            * focal_length
            * (lams)
            / (self.n1)
            / fs
            / fs
        )
        fs = fs.cpu().tolist()
        for f in fs:
            self.bluesteins_y.append(
                BluesteinDFT(
                    f / 2 + self.yrange[0],
                    f / 2 + self.yrange[1],
                    f,
                    self.Mouty,
                    Min,
                    device=device,
                )
            )
            self.bluesteins_x.append(
                BluesteinDFT(
                    f / 2 + self.xrange[0],
                    f / 2 + self.xrange[1],
                    f,
                    self.Moutx,
                    Min,
                    device=device,
                )
            )
        self.E_ideals = torch.ones_like(self.lams)
        self.R = torch.stack(
            [
                -torch.sin(self.th) * torch.cos(self.phi),
                -torch.sin(self.th) * torch.sin(self.phi),
                torch.cos(self.th),
            ],
            dim=-1,
        )
        self.R = self.R.unsqueeze(-2)

    def __call__(self, E, correct=False):
        # The input E has shape (batch, x, y, 2, lam),
        # where the z-component is not included.
        # The output E has shape (batch, x, y, z, 3, lam).
        # For different wavelengths (lam), a simple for-loop is used for now.

        Ex_in, Ey_in = E[..., 0:1, :], E[..., 1:2, :]
        th = self.th.unsqueeze(-1).unsqueeze(-1)
        phi = self.phi.unsqueeze(-1).unsqueeze(-1)
        z_arr = self.z_arr.unsqueeze(0).unsqueeze(0).unsqueeze(-1)
        k0, n1 = self.k0.view(1, 1, 1, -1), self.n1

        costh = torch.cos(th)
        _sqrt_costh = self._sqrt_costh.unsqueeze(-1)
        phase = torch.exp(1j * k0 * n1 * z_arr * costh)
        deltadim = 0
        C = (self.C / self.E_ideals).view(1, 1, 1, -1)
        E_out = torch.zeros(
            [self.Moutx, self.Mouty, self.z_arr.numel(), 3, self.lams.numel()],
            dtype=torch.complex64,
            device=self.device,
        )
        if E.dim() == 5:
            th = th.unsqueeze(0)
            phi = phi.unsqueeze(0)
            z_arr = z_arr.unsqueeze(0)
            k0 = k0.unsqueeze(0)
            costh = costh.unsqueeze(0)
            _sqrt_costh = _sqrt_costh.unsqueeze(0)
            phase = phase.unsqueeze(0)
            C = C.unsqueeze(0)
            deltadim = 1
            E_out = torch.zeros(
                [
                    E.size(0),
                    self.Moutx,
                    self.Mouty,
                    self.z_arr.numel(),
                    3,
                    self.lams.numel(),
                ],
                dtype=torch.complex64,
                device=self.device,
            )
        Ex = (
            (
                Ex_in * (1 + (costh - 1) * torch.cos(phi) ** 2)
                + Ey_in * (costh - 1) * torch.cos(phi) * torch.sin(phi)
            )
            * phase
            * _sqrt_costh
        )

        Ey = (
            (
                Ex_in * (costh - 1) * torch.cos(phi) * torch.sin(phi)
                + Ey_in * (1 + (costh - 1) * torch.sin(phi) ** 2)
            )
            * phase
            * _sqrt_costh
        )

        Ez = (
            (Ex_in * torch.cos(phi) + Ey_in * torch.sin(phi))
            * torch.sin(th)
            * phase
            * _sqrt_costh
        )
        if correct:
            temp = torch.stack([Ex, Ey, Ez], dim=-1)
            temp = temp - 0.5 * self.R * torch.sum(self.R * temp, dim=-1, keepdim=True)
            Ex, Ey, Ez = temp[:, :, :, 0], temp[:, :, :, 1], temp[:, :, :, 2]
        for i in range(self.lams.numel()):
            E_out[..., 0, i] = self.bluesteins_x[i].transform(
                self.bluesteins_y[i].transform(Ex[..., i], dim=1 + deltadim),
                dim=0 + deltadim,
            )
            E_out[..., 1, i] = self.bluesteins_x[i].transform(
                self.bluesteins_y[i].transform(Ey[..., i], dim=1 + deltadim),
                dim=0 + deltadim,
            )
            E_out[..., 2, i] = self.bluesteins_x[i].transform(
                self.bluesteins_y[i].transform(Ez[..., i], dim=1 + deltadim),
                dim=0 + deltadim,
            )

        return C * E_out

    def Get_Z_offset_Phase(self, z):
        k0, n1 = self.k0, self.n1
        costh = torch.cos(self.th)
        phase = k0.view(1, 1, -1) * n1 * z * (-costh).unsqueeze(-1)
        return phase
