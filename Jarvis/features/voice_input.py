import importlib.util

import speech_recognition as sr

try:
    import numpy as np
except Exception:
    np = None

try:
    import sounddevice as sd
except Exception:
    sd = None


class VoiceInputService:
    def __init__(self, config):
        self.voice_input_enabled = getattr(config, 'voice_input_enabled', True)
        self.voice_retry_limit = getattr(config, 'voice_retry_limit', 2)
        self.keyboard_fallback = getattr(config, 'keyboard_fallback', True)
        self.microphone_device_index = getattr(config, 'microphone_device_index', None)
        self.microphone_timeout = getattr(config, 'microphone_timeout', 5)
        self.microphone_phrase_time_limit = getattr(config, 'microphone_phrase_time_limit', 10)
        self.microphone_adjust_for_ambient = getattr(config, 'microphone_adjust_for_ambient', True)
        self.microphone_ambient_duration = getattr(config, 'microphone_ambient_duration', 0.8)
        self.voice_recognition_language = getattr(config, 'voice_recognition_language', 'en-US')
        self.energy_threshold = getattr(config, 'voice_energy_threshold', 300)
        self.dynamic_energy_threshold = getattr(config, 'voice_dynamic_energy_threshold', True)
        self.voice_input_backend = getattr(config, 'voice_input_backend', 'auto')
        self.voice_sample_rate = getattr(config, 'voice_sample_rate', 16000)
        self.pyaudio_available = importlib.util.find_spec('pyaudio') is not None
        self.voice_runtime_available = self.voice_input_enabled

    def list_microphones_with_diagnostics(self):
        microphones = []
        diagnostics = {
            'backend': None,
            'errors': [],
        }

        if sd is not None:
            try:
                diagnostics['backend'] = 'sounddevice'
                devices = sd.query_devices()
                for index, device in enumerate(devices):
                    if int(device.get('max_input_channels', 0)) > 0:
                        name = str(device.get('name', f'Device {index}')).strip()
                        microphones.append((index, name))
            except Exception as error:
                diagnostics['errors'].append(f"sounddevice: {error}")
                print(f"Microphone list error (sounddevice): {error}")

        if microphones:
            return microphones, diagnostics

        # Fallback path for SpeechRecognition only when PyAudio exists.
        if not self.pyaudio_available:
            if diagnostics['backend'] is None:
                diagnostics['backend'] = 'none'
            diagnostics['errors'].append('pyaudio not installed; speech_recognition microphone listing unavailable')
            return microphones, diagnostics

        try:
            diagnostics['backend'] = diagnostics['backend'] or 'speech_recognition'
            names = sr.Microphone.list_microphone_names()
            for index, name in enumerate(names):
                microphones.append((index, str(name).strip()))
        except Exception as error:
            diagnostics['errors'].append(f"speech_recognition: {error}")
            print(f"Microphone list error (speech_recognition): {error}")

        return microphones, diagnostics

    def list_microphones(self):
        microphones, _ = self.list_microphones_with_diagnostics()
        return microphones

    def set_microphone_device(self, device_index):
        if device_index is None:
            self.microphone_device_index = None
            return True

        try:
            self.microphone_device_index = int(device_index)
            return True
        except Exception:
            return False

    def _text_fallback_input(self, prompt="Type command: "):
        try:
            return input(prompt).strip().lower()
        except Exception:
            return False

    def mic_input(self):
        if not self.voice_runtime_available:
            return self._text_fallback_input()

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
        recognizer.energy_threshold = self.energy_threshold
        attempts = 0

        while attempts <= self.voice_retry_limit:
            try:
                audio = self._capture_audio(recognizer)

                print("Recognizing...")
                command = recognizer.recognize_google(
                    audio,
                    language=self.voice_recognition_language,
                ).lower()
                print(f'You said: {command}')
                return command
            except sr.WaitTimeoutError:
                print("Listening timed out. No speech detected.")
                attempts += 1
                if attempts <= self.voice_retry_limit:
                    print("Retrying microphone capture...")
            except sr.UnknownValueError:
                print("I could not understand the audio input.")
                attempts += 1
                if attempts <= self.voice_retry_limit:
                    print("Retrying voice recognition...")
            except OSError as error:
                print(f"Microphone device error: {error}")
                if self.keyboard_fallback:
                    print("Falling back to keyboard input.")
                    self.voice_runtime_available = False
                    return self._text_fallback_input()
                return False
            except Exception as error:
                print(error)
                attempts += 1
                if attempts <= self.voice_retry_limit:
                    print("Voice input failed, retrying...")

        if self.keyboard_fallback:
            print("Voice input unavailable. Falling back to keyboard input.")
            self.voice_runtime_available = False
            return self._text_fallback_input()

        return False

    def _capture_audio(self, recognizer):
        backend = (self.voice_input_backend or 'auto').lower()

        if backend == 'auto':
            if sd is not None and np is not None:
                audio = self._capture_audio_sounddevice()
                if audio:
                    return audio
            if self.pyaudio_available:
                with sr.Microphone(device_index=self.microphone_device_index) as source:
                    print("Listening....")
                    if self.microphone_adjust_for_ambient:
                        recognizer.adjust_for_ambient_noise(
                            source,
                            duration=self.microphone_ambient_duration,
                        )
                    return recognizer.listen(
                        source,
                        timeout=self.microphone_timeout,
                        phrase_time_limit=self.microphone_phrase_time_limit,
                    )
            raise OSError("No working microphone backend found. sounddevice is required when PyAudio is unavailable.")

        if backend == 'sounddevice':
            audio = self._capture_audio_sounddevice()
            if audio:
                return audio
            raise OSError('sounddevice audio capture failed')

        if backend == 'pyaudio':
            if not self.pyaudio_available:
                raise OSError('PyAudio is not installed. Set voice_input_backend to "sounddevice".')
            with sr.Microphone(device_index=self.microphone_device_index) as source:
                print("Listening....")
                if self.microphone_adjust_for_ambient:
                    recognizer.adjust_for_ambient_noise(
                        source,
                        duration=self.microphone_ambient_duration,
                    )
                return recognizer.listen(
                    source,
                    timeout=self.microphone_timeout,
                    phrase_time_limit=self.microphone_phrase_time_limit,
                )

        raise OSError(f"Unsupported voice_input_backend: {self.voice_input_backend}")

    def _capture_audio_sounddevice(self):
        if sd is None or np is None:
            return None

        print("Listening....")
        duration = max(float(self.microphone_phrase_time_limit), 1.0)
        device = self.microphone_device_index

        try:
            if device is not None:
                sd.query_devices(device)
        except Exception as error:
            raise OSError(f"Invalid microphone device index: {device}. {error}") from error

        candidate_sample_rates = []
        configured_rate = int(self.voice_sample_rate)
        if configured_rate > 0:
            candidate_sample_rates.append(configured_rate)

        try:
            default_info = sd.query_devices(device)
            default_rate = int(float(default_info.get('default_samplerate', 0)))
            if default_rate > 0 and default_rate not in candidate_sample_rates:
                candidate_sample_rates.append(default_rate)
        except Exception:
            pass

        for fallback_rate in (16000, 44100, 48000):
            if fallback_rate not in candidate_sample_rates:
                candidate_sample_rates.append(fallback_rate)

        last_error = None
        for sample_rate in candidate_sample_rates:
            try:
                sd.check_input_settings(device=device, channels=1, dtype='int16', samplerate=sample_rate)
                frames = int(sample_rate * duration)
                recording = sd.rec(
                    frames,
                    samplerate=sample_rate,
                    channels=1,
                    dtype='int16',
                    device=device,
                )
                sd.wait()

                audio_bytes = recording.tobytes()
                if audio_bytes:
                    return sr.AudioData(audio_bytes, sample_rate, 2)
            except Exception as error:
                last_error = error
                continue

        raise OSError(
            f"sounddevice capture failed for device {device} with tested sample rates {candidate_sample_rates}. "
            f"Last error: {last_error}"
        )
