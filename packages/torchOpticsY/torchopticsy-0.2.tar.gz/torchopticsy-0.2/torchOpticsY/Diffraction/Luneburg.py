import torch
import torch.nn.functional as F


def fft_circular_conv2d(E, G):
    E_fft = torch.fft.fft2(E.permute(2, 0, 1))
    G_fft = torch.fft.fft2(G.permute(2, 0, 1))
    C_fft = E_fft * G_fft
    C_ifft = torch.fft.ifft2(C_fft).permute(1, 2, 0)
    return C_ifft


class Luneburg:
    # The calculation method for Ez is different and omitted here.
    # The sampling theorem must be satisfied: T < lambda / 2
    def __init__(
        self,
        uv_len,  # Integration region
        x_range,
        y_range,
        z_range,
        sampling_interval,  # Sampling interval, a 1D array; strictly followed in xy-directions,
        # while z-direction is adaptively adjusted
        lams,
        focal_length,  # Evaluation is based on this focal length
        n1=1,
        scale=1,  # Integer > 1, used to represent a reduced sampling frequency for E
        device="cuda",
    ):
        self.device = device
        self.scale = scale
        lams = torch.tensor(lams, device=device)
        self.lams = lams
        self.k = 2 * torch.pi * n1 / self.lams
        self.n1 = n1
        self.focal_length = focal_length
        uv_len = uv_len - sampling_interval[0]
        ux_arr = torch.arange(
            -uv_len / 2 + x_range[0] - sampling_interval[0],
            x_range[1] + uv_len / 2,
            step=sampling_interval[0],
            device=device,
        )

        vy_arr = torch.arange(
            -uv_len / 2 + y_range[0] - sampling_interval[1],
            y_range[1] + uv_len / 2,
            step=sampling_interval[1],
            device=device,
        )
        z_arr = torch.linspace(
            z_range[0] + focal_length,
            z_range[1] + focal_length,
            int((z_range[1] - z_range[0]) / sampling_interval[2] / 2) * 2 + 1,
            device=device,
        )

        center = (
            round((x_range[0] + x_range[1]) / 2 / sampling_interval[0])
            * sampling_interval[0]
        )
        u_arr = ux_arr - center
        u_start_id = torch.argmin(torch.abs(u_arr + uv_len / 2))
        u_end_id = torch.argmin(torch.abs(u_arr - uv_len / 2))
        u_arr = u_arr[u_start_id : u_end_id + 1 : scale] + sampling_interval[0] / 2
        du = torch.mean(u_arr)
        u_arr = u_arr - du
        center = (
            round((y_range[0] + y_range[1]) / 2 / sampling_interval[1])
            * sampling_interval[1]
        )
        v_arr = vy_arr - center
        v_start_id = torch.argmin(torch.abs(v_arr + uv_len / 2))
        v_end_id = torch.argmin(torch.abs(v_arr - uv_len / 2))
        v_arr = v_arr[v_start_id : v_end_id + 1 : scale] + sampling_interval[1] / 2
        dv = torch.mean(v_arr)
        v_arr = v_arr - dv

        x_start_id = torch.argmin(torch.abs(ux_arr - x_range[0]))
        x_end_id = torch.argmin(torch.abs(ux_arr - x_range[1]))
        y_start_id = torch.argmin(torch.abs(vy_arr - y_range[0]))
        y_end_id = torch.argmin(torch.abs(vy_arr - y_range[1]))

        x_arr = ux_arr[x_start_id : x_end_id + 1] - du
        y_arr = vy_arr[y_start_id : y_end_id + 1] - dv

        co_public = (
            -1j
            * sampling_interval[0]
            * sampling_interval[1]
            * n1
            / self.lams.view(1, 1, 1, -1)
        )  # / 4 / torch.pi
        R_q = torch.sqrt(
            (ux_arr.view(-1, 1, 1, 1)) ** 2
            + (vy_arr.view(1, -1, 1, 1)) ** 2
            + z_arr.view(1, 1, -1, 1) ** 2
        )
        G_2D = self.k * R_q * 1j
        G_2D = torch.exp(G_2D) / R_q**2 * co_public * (1 - 1 / G_2D)

        self.G_2D = G_2D

        self.u_arr = u_arr
        self.v_arr = v_arr
        self.x_arr = x_arr
        self.y_arr = y_arr
        self.z_arr = z_arr

        self.x_num = x_end_id - x_start_id + 1
        self.y_num = y_end_id - y_start_id + 1

        self.u_pad_num = ux_arr.numel() - u_arr.numel() * scale
        self.v_pad_num = vy_arr.numel() - v_arr.numel() * scale
        self.dS = sampling_interval[0] * sampling_interval[1]

    def __call__(self, E):
        # E should have shape (u, v, lam)
        if E.dim() == 3:
            E_padded = E.repeat_interleave(self.scale, dim=0)
            E_padded = E_padded.repeat_interleave(self.scale, dim=1)
            pad = (
                0,
                0,  # No padding applied to the 2nd dimension (D2)
                self.v_pad_num,
                0,  # Extend on both sides of the 1st dimension (D1)
                self.u_pad_num,
                0,  # Extend on both sides of the 0th dimension (D0)
            )

            E_padded = F.pad(E_padded, pad, mode="constant", value=0)
            E_out = torch.zeros(
                [
                    self.x_num,
                    self.y_num,
                    self.z_arr.numel(),
                    self.lams.numel(),
                ],
                device=self.device,
                dtype=torch.complex64,
            )
            for z in range(self.z_arr.numel()):
                E_out[:, :, z, :] = fft_circular_conv2d(
                    E_padded, self.G_2D[:, :, z] * self.z_arr[z]
                )[
                    : self.x_num,
                    : self.y_num,
                ]
            return E_out

    def Get_G_2D(self, x_f, y_f, z_f):  # Typically used for optimization and validation
        z = self.focal_length + z_f  # Detection coordinate
        co_public = (
            -1j * self.dS * self.n1 / self.lams * self.scale**2
        )  # / 4 / torch.pi
        R_q = torch.sqrt(
            z**2
            + (x_f - self.u_arr.view(-1, 1, 1)) ** 2
            + (y_f - self.v_arr.view(1, -1, 1)) ** 2
        )
        ik0R = self.k.view(1, 1, -1) * R_q * 1j
        G_2D = torch.exp(ik0R) / R_q**2 * (1 - 1 / ik0R) * co_public

        return z * G_2D
