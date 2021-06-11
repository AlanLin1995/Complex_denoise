# -*- coding: utf-8 -*-
import numpy as np
import model
import cv2, sys
import tensorflow as tf
import os
from skimage.measure import compare_psnr


sigma = 25
model_path = './model/'
model_name = 'Comp_model_blind_rand_weight_'
test_img_dir_BSD68 = './dataset/dncnn-img/test/BSD68/'
test_img_files_BSD68 = os.listdir(test_img_dir_BSD68)
test_img_dir_set12 = './dataset/dncnn-img/test/Set12/'
test_img_files_set12 = os.listdir(test_img_dir_set12)


def post_process(img):
    img = np.squeeze(img)
    img = img * 255
    img = np.clip(img, 0, 255)
    img = img.astype(np.uint8)
    return img


def psnr(img1, img2):
    img1 = np.clip(img1, 0, 255)

    img2 = np.clip(img2, 0, 255)

    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)

    if(len(img1.shape) == 2):
        m, n = img1.shape
        k = 1
    elif (len(img1.shape) == 3):
        m, n, k = img1.shape

    B = 8
    diff = np.power(img1 - img2, 2)
    MAX = 2**B - 1
    MSE = np.sum(diff) / (m * n * k)
    sqrt_MSE = np.sqrt(MSE)
    PSNR = 20 * np.log10(MAX / sqrt_MSE)

    return PSNR


def eval_12():
    set_num = 12
    psnr_for_each = np.zeros(set_num)
    ssim_for_each = np.zeros(set_num)
    with tf.Graph().as_default():
        tf.set_random_seed(19940308)
        img_clean = tf.placeholder(tf.float32, [None, None, None, 1], name='clean_image')
        training = tf.placeholder(tf.bool, name='is_training')
        img_noise = img_clean + tf.random_normal(shape=tf.shape(img_clean), stddev=sigma / 255.0)
        img_imag = tf.zeros(shape=tf.shape(img_clean))
        Y = model.inference(img_noise, img_imag, is_training=training)

        var_list = [v for v in tf.all_variables() if v.name.startswith('ComplexNet')]
        saver = tf.train.Saver(var_list)

        with tf.Session() as sess:
            saver.restore(sess, model_path + model_name + ".ckpt")

            for j in range(set_num):
                num = 5
                test_img = test_img_dir_set12 + test_img_files_set12[j]
                out = [0] * num
                psnrs = np.zeros(num)

                img_raw = cv2.imread(test_img, 0)
                img = img_raw.astype(np.float32) / 255
                img = np.expand_dims(img, axis=0)
                img = np.expand_dims(img, axis=3)

                # ssims = np.zeros(5)
                for i in range(num):
                    out[i], = sess.run([Y], feed_dict={img_clean: img, training: False})
                    psnrs[i] = compare_psnr(np.squeeze(img), np.squeeze(out[i]))
                    out[i] = post_process(out[i])
                    # psnrs[i] = psnr(out[i], img_raw)
                    # ssims[i] = Psnr.ssim(out[i], img_raw)
                psnr_for_each[j] = sum(psnrs) /len(psnrs)
                # ssim_for_each[j] = max(ssims)
            print(np.mean(psnr_for_each))
    # log.logging('log.txt', 'On set12, psnr for num ' + str(num) + ': '+str(np.mean(psnr_for_each)))
    # print(np.mean(ssim_for_each))
    # log.logging('log.txt', 'On set12, ssim for num ' + str(num) + ': '+str(np.mean(ssim_for_each)))


def eval_68():
    set_num = 68
    psnr_for_each = np.zeros(set_num)
    ssim_for_each = np.zeros(set_num)
    with tf.Graph().as_default():
        tf.set_random_seed(19940308)
        img_clean = tf.placeholder(tf.float32, [None, None, None, 1], name='clean_image')
        training = tf.placeholder(tf.bool, name='is_training')
        img_noise = img_clean + tf.random_normal(shape=tf.shape(img_clean), stddev=sigma / 255.0)
        img_imag = tf.zeros(shape=tf.shape(img_clean))
        Y = model.inference(img_noise, img_imag, is_training=training)

        var_list = [v for v in tf.all_variables() if v.name.startswith('ComplexNet')]
        saver = tf.train.Saver(var_list)

        with tf.Session() as sess:
            saver.restore(sess, model_path + model_name + ".ckpt")

            for j in range(set_num):
                num = 5
                test_img = test_img_dir_BSD68 + test_img_files_BSD68[j]
                out = [0] * num
                psnrs = np.zeros(num)

                img_raw = cv2.imread(test_img, 0)
                w, h = img_raw.shape
                if w % 2 != 0:
                    w_new = w - 1
                else:
                    w_new = w
                if h % 2 != 0:
                    h_new = h - 1
                else:
                    h_new = h
                img_raw = img_raw[:w_new, :h_new]
                img = img_raw.astype(np.float32) / 255
                img = np.expand_dims(img, axis=0)
                img = np.expand_dims(img, axis=3)

                # ssims = np.zeros(5)
                for i in range(num):
                    out[i], = sess.run([Y], feed_dict={img_clean: img, training: False})
                    psnrs[i] = compare_psnr(np.squeeze(img), np.squeeze(out[i]))
                    out[i] = post_process(out[i])
                    # psnrs[i] = psnr(out[i], img_raw)
                    # ssims[i] = Psnr.ssim(out[i], img_raw)
                psnr_for_each[j] = sum(psnrs) /len(psnrs)
                # ssim_for_each[j] = max(ssims)
            print(np.mean(psnr_for_each))


if __name__ == '__main__':
    eval_12()
    eval_68()

