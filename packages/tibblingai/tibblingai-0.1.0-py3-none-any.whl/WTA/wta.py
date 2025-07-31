import os
import numpy as np
import pickle
import sys

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import tensorflow_addons as tfa

@tf.function
def LCD_mc_full(image, kernal_size=3, stride=1):
    tf_a = image
    img_shape = tf.shape(tf_a)
    s0 = tf.shape(tf_a)[0]
    s1i = tf.shape(tf_a)[1]
    s2i = tf.shape(tf_a)[2]
    s3 = tf.shape(tf_a)[3]
    pd = kernal_size - 2
    paddings = tf.constant([[0, 0], [pd, pd], [pd, pd], [0, 0]])
    tf_a1 = tf.pad(tf_a, paddings, "SYMMETRIC")
    yy = tf.image.extract_patches(tf_a1, sizes=[1, kernal_size, kernal_size, 1], strides=[1, stride, stride, 1], rates=4 * [1], padding='SAME')
    s1 = tf.shape(yy)[1]
    s2 = tf.shape(yy)[2]
    patches = tf.reshape(yy, [-1, s1 * s2, kernal_size * kernal_size, s3])
    at = tf.transpose(patches, perm=[0, 3, 1, 2])
    yy = tf.cast(at, dtype=tf.float32)
    ll = tf.math.reduce_std(yy, axis=3)
    llt = tf.transpose(ll, perm=[0, 2, 1])
    oo1 = tf.reshape(llt, (-1, s1, s2, s3))
    oo2 = tf.image.crop_to_bounding_box(oo1, pd, pd, s1i, s2i)
    a = tf.reshape(oo2, [s0, s1i * s2i * s3])
    b = tf.reduce_max(a, axis=1)
    oo = a / tf.reshape(b, [-1, 1])
    oo3 = tf.reshape(oo, (-1, s1i, s2i, s3))
    oo5 = tf.reshape(oo3, tf.shape(tf_a))
    return oo5


@tf.function
def fspecial_gauss(image, size, sigma):
    return tfa.image.gaussian_filter2d(
        image,
        filter_shape=(size, size),
        sigma=sigma,
        padding='REFLECT',
        constant_values=0,
        name=None
    )


@tf.function
def ssim_struct(X,
                data_range=1.0,
                size=25,
                sigma=0.5,
                pad=1,
                size_average=True,
                K=(0.01, 0.03)):
    Y = X
    K1, K2 = K
    compensation = 1.0
    C1 = (K1 * data_range) ** 2
    C2 = (K2 * data_range) ** 2
    C3 = C2 / 2
    mu1 = fspecial_gauss(X, size, sigma)
    mu2 = fspecial_gauss(Y, size, sigma)
    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = compensation * (fspecial_gauss(X * X, size, sigma) - mu1_sq)
    sigma2_sq = compensation * (fspecial_gauss(Y * Y, size, sigma) - mu2_sq)
    sigma12 = compensation * (fspecial_gauss(X * Y, size, sigma) - mu1_mu2)
    cont = (((2 * sigma1_sq * sigma2_sq) + C2) / (sigma1_sq + sigma2_sq + C2))
    struc = ((sigma12 + C3) / ((sigma1_sq * sigma2_sq) + C3))
    cs_map = (2 * sigma12 + C2) / (sigma1_sq + sigma2_sq + C2)
    ssim_map = struc
    ssim_per_channel = tf.reshape(ssim_map, tf.shape(X))
    s0 = ssim_per_channel.shape[0]
    s1 = ssim_per_channel.shape[1]
    s2 = ssim_per_channel.shape[2]
    s3 = ssim_per_channel.shape[3]
    a = tf.reshape(ssim_per_channel, [-1, s1 * s2 * s3])
    b = tf.reduce_max(a, axis=1)
    oo = a / tf.reshape(b, [-1, 1])
    ssim_per_channel1 = tf.reshape(oo, tf.shape(X))
    return ssim_per_channel1


def all_fcn(image,lc_neighbours=4, lc_stride=1, st_data_range=1.0, st_win=11 , st_sigma =2, gauss_win=11, gauss_sigma=1, LC_en=True, ST_en=False, G_en=False, **kwargs):

    outputs = []

    x = LCD_mc_full(image,lc_neighbours,lc_stride) if LC_en else image
    x1 = ssim_struct(x,st_data_range,st_win,st_sigma) if ST_en else x
    x2 = fspecial_gauss(x1,gauss_win, gauss_sigma) if G_en else x1

    return x2

def preprocessing(img: np.ndarray) -> np.ndarray:
    """
    Ensures input NumPy image has shape (1, H, W, 3):
    - Converts grayscale to RGB by repeating channels
    - Adds batch dimension if missing
    """
    if img.ndim == 2:
        # (H, W) → (H, W, 1)
        img = img[..., np.newaxis]

    if img.ndim == 3:
        if img.shape[-1] == 1:
            # (H, W, 1) → (H, W, 3)
            img = np.repeat(img, 3, axis=-1)
        elif img.shape[-1] != 3:
            raise ValueError(f"Unsupported channel count: {img.shape[-1]}. Expected 1 or 3.")

        # Add batch dimension: (H, W, 3) → (1, H, W, 3)
        img = img[np.newaxis, ...]

    elif img.ndim == 4:
        if img.shape[-1] == 1:
            # (B, H, W, 1) → (B, H, W, 3)
            img = np.repeat(img, 3, axis=-1)
        elif img.shape[-1] != 3:
            raise ValueError(f"Unsupported channel count: {img.shape[-1]}. Expected 1 or 3.")
        # already batched

    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")

    return img


def normalize(data):
    original_post = (data - np.mean(data))/np.std(data)
    original_post = (original_post - np.min(original_post))/(np.max(original_post) - np.min(original_post))

    return original_post


def wta(image, lc_neighbours=3, lc_stride=1, st_data_range=1.0, st_win=11 , st_sigma =.3, gauss_win=11, gauss_sigma=0.3, LC_en=True, ST_en=False, G_en=False):
    preprocessed_image = preprocessing(image)
    x_out =all_fcn((preprocessed_image [...]),
                    lc_neighbours=lc_neighbours, lc_stride=lc_stride, st_data_range=st_data_range, st_win=st_win , st_sigma =st_sigma, gauss_win=gauss_win, 
                    gauss_sigma=gauss_sigma, LC_en=LC_en, ST_en=ST_en, G_en=G_en)

    return x_out[...,0]





