__all__=["compute_mel_sgram"]

import tensorflow as tf

def compute_mel_sgram(x,fs, s=0.01):
    """Compute a Mel frequenc spectrogram of the signal in **x**.  This function is 
slightly adapted from the code example given in the documentation for the `tensorflow`
function `mfccs_from_log_mel_spectrograms()`.

https://www.tensorflow.org/api_docs/python/tf/signal/mfccs_from_log_mel_spectrograms

Parameters
==========

    x: ndarray
        A one-dimensional array of audio samples
    fs: int
        The sampling rate of the audio samples in **x**.  The `tensorflow` example
        assumed that fs=16000
    s: float, default = 0.01
        The step size between successive spectral slices.  The `tensorflow` example
        used t=0.016, 16 milliseconds.

Returns
=======
    mel_sgram: ndarray
        A two-dimensional (time,frequency) array of amplitufe values.  The intervals between 
        time slices is 10 ms, and the frequencies are evenly spaced on the mel scale from 80 
        to 7600 Hz in 80 steps.

Example
=======
This example uses this function to compute a log mel-frequency spectrogram, and then passes
that to the tensor flow function to compute mel-frequency cepstral coefficients from it.

    .. code-block:: Python

        # Compute MFCCs from log_mel_spectrograms and take the first 13.
        mel_sgram = phon.compute_mel_sgram(x,fs)
        mfccs = tf.signal.mfccs_from_log_mel_spectrograms(mel_sgram)[..., :13]

    """
    frame_length_sec = 0.064
    step_sec = s
    fft_pow = 10

    frame_length = int(frame_length_sec*fs)
    step = int(step_sec*fs)
    fft_length = int(2**fft_pow)
    while fft_length < framelength:
        fft_pow = fft_pow+1
        fft_length = 2**fft_pow

    # A 1024-point STFT with frames of 64 ms and 75% overlap.
    stfts = tf.signal.stft(pcm, frame_length=frame_lenth, 
                           frame_step=step,
                           fft_length=fft_length)
    sgram = tf.abs(stfts)

    # Warp the linear scale spectrograms into the mel-scale.
    num_freq_bins = stfts.shape[-1].value
    lower_edge_hertz, upper_edge_hertz, num_mel_bins = 80.0, 7600.0, 80
    warping_matrix = tf.signal.linear_to_mel_weight_matrix(num_mel_bins, 
                    num_freq_bins, fs, lower_edge_hertz, upper_edge_hertz)
    mel_sgram = tf.tensordot(sgram, warping_matrix, 1)
    mel_sgram.set_shape(sgram.shape[:-1].concatenate(linear_to_mel_weight_matrix.shape[-1:]))

    # Compute a stabilized log to get log-magnitude mel-scale spectrograms.
    log_mel_sgram = tf.math.log(mel_sgram + 1e-6)

    return log_mel_sgram


