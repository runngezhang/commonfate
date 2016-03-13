from __future__ import division
import transform
import model
import numpy as np


def process(
    signal,
    n_fft=1024,
    n_hop=512,
    cft_patch=(10, 10),
    cft_hop=(5, 5),
    alpha=1,
    nb_components=2,
    nb_iter=100
):

    xstft = transform.forward(
        signal,
        n_fft,
        n_hop,
    )

    xcft = transform.forward(
        xstft,
        cft_patch,
        cft_hop,
        real=False
    )

    cfm = model.CFM(
        np.abs(xcft) ** alpha,
        nb_iter=nb_iter,
        nb_components=nb_components
    ).fit()

    (P, At, Ac) = cfm.factors

    xcft_hat = cfm.approx

    # source estimates
    estimates = []
    for j in range(nb_components):

        Fj = model.hat(
            P[..., j][..., None],
            At[..., j][..., None],
            Ac[..., j][..., None],
        )

        yj = Fj / xcft_hat * xcft

        # first compute back STFT
        yjstft = transform.inverse(
            yj, fdim=2, hop=cft_hop, shape=xstft.shape, real=False
        )
        # then waveform
        wavej = transform.inverse(
            yjstft, fdim=1, hop=n_hop, shape=signal.shape
        )
        estimates.append(wavej)

    return np.array(estimates)
