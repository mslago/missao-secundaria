using System;
using System.Linq;
using NAudio.Wave;
using ScottPlot;
using MathNet.Numerics;
using MathNet.Numerics.IntegralTransforms;
using System.Numerics;

class Program
{
    static void Main(string[] args)
    {
        string audioFilePath = "audiofile.wav";

        // Read the audio file
        using (var audioFileReader = new AudioFileReader(audioFilePath))
        {
            int sampleRate = audioFileReader.WaveFormat.SampleRate;
            int blockAlign = audioFileReader.WaveFormat.BlockAlign;

            int totalSamples = (int)(audioFileReader.TotalTime.TotalSeconds * sampleRate);
            int alignedSamples = (totalSamples / blockAlign) * blockAlign;
            float[] samples = ReadAudioSamples(audioFileReader);

            // Apply a Hann window to reduce spectral leakage
            ApplyHannWindow(samples);

            // Perform FFT
            var fftValues = ComputeFFT(samples);

            // Find the most prominent frequency above 300 Hz
            double maxFrequency = FindMostProminentFrequency(fftValues, sampleRate, 300);

            // Plot the results
            PlotFFTAndHighlightMaxFrequency(fftValues, sampleRate, maxFrequency);

            Console.WriteLine($"The most prominent frequency is: {maxFrequency:F2} Hz");
        }
    }

    static float[] ReadAudioSamples(AudioFileReader audioFileReader)
    {
        int bytesPerSample = audioFileReader.WaveFormat.BitsPerSample / 8; // Typically 2 bytes for 16-bit audio
        int blockAlign = audioFileReader.WaveFormat.BlockAlign;           // Block alignment (e.g., 4 bytes for stereo 16-bit)
        int totalBytes = (int)(audioFileReader.Length);                   // Total bytes in the audio file
        int totalSamples = totalBytes / bytesPerSample;                   // Total samples in the audio file

        // Ensure buffer size is aligned to the block size
        if (totalBytes % blockAlign != 0)
        {
            totalSamples -= totalSamples % (blockAlign / bytesPerSample);
        }

        float[] samples = new float[totalSamples];
        int readSamples = 0;

        // Read samples into the buffer
        while (readSamples < totalSamples)
        {
            int samplesToRead = Math.Min(totalSamples - readSamples, 1024); // Read in chunks
            readSamples += audioFileReader.Read(samples, readSamples, samplesToRead);
        }

        return samples;
    }


    static void ApplyHannWindow(float[] samples)
    {
        for (int i = 0; i < samples.Length; i++)
        {
            samples[i] *= (float)(0.5 * (1 - Math.Cos(2 * Math.PI * i / (samples.Length - 1))));
        }
    }

    static Complex[] ComputeFFT(float[] samples)
    {
        int fftLength = (int)Math.Pow(2, Math.Ceiling(Math.Log(samples.Length, 2))); // Next power of 2
        var complexSamples = new Complex[fftLength];

        for (int i = 0; i < samples.Length; i++)
        {
            complexSamples[i] = new Complex(samples[i], 0); // Real part is the sample, imaginary part is 0
        }

        // Zero-pad remaining FFT values
        for (int i = samples.Length; i < fftLength; i++)
        {
            complexSamples[i] = Complex.Zero;
        }

        Fourier.Forward(complexSamples, FourierOptions.Matlab);
        return complexSamples;
    }

    static double FindMostProminentFrequency(Complex[] fftValues, int sampleRate, double minFrequency)
    {
        int fftSize = fftValues.Length;
        double binSize = sampleRate / (double)fftSize;

        int maxIndex = 0;
        double maxAmplitude = 0.0;

        for (int i = 1; i < fftValues.Length / 2; i++) // Consider only positive frequencies
        {
            double frequency = i * binSize;
            double amplitude = fftValues[i].Magnitude;

            if (frequency > minFrequency && amplitude > maxAmplitude)
            {
                maxIndex = i;
                maxAmplitude = amplitude;
            }
        }

        return maxIndex * binSize; // Frequency corresponding to the bin
    }

    static void PlotFFTAndHighlightMaxFrequency(Complex[] fftValues, int sampleRate, double maxFrequency)
    {
        // Create the plot
        var plt = new ScottPlot.Plot();
        plt.Resize(600, 400);

        // Extract frequencies and amplitudes from FFT values
        int fftSize = fftValues.Length;
        double binSize = sampleRate / (double)fftSize;
        var frequencies = Enumerable.Range(0, fftSize / 2).Select(i => i * binSize).ToArray();
        var magnitudes = fftValues.Take(fftSize / 2).Select(c => c.Magnitude).ToArray();

        // Add scatter plot for FFT
        var scatter = plt.AddScatter(frequencies, magnitudes);
        scatter.Label = "FFT";

        // Add vertical line for the most prominent frequency
        var vline = plt.AddVerticalLine(maxFrequency);
        vline.Color = System.Drawing.Color.Red;
        vline.LineStyle = ScottPlot.LineStyle.Dash;
        vline.Label = $"Max Frequency: {maxFrequency:F2} Hz";

        // Customize the plot
        plt.Title("FFT of Audio File");
        plt.XLabel("Frequency (Hz)");
        plt.YLabel("Amplitude");
        plt.Legend();

        // Save the plot to a file
        plt.SaveFig("fft_plot.png");
    }
}
