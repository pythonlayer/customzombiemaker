import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import numpy as np

try:
    import librosa
    import mido
    import sounddevice as sd
    import soundfile as sf
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency. Install with:\n"
        "pip install sounddevice soundfile librosa mido numpy\n"
        f"\nDetails: {exc}"
    )


def audio_to_note_events(
    audio: np.ndarray,
    sample_rate: int,
    hop_length: int = 128,
    frame_length: int = 2048,
    fmin: float = 65.41,  # C2
    fmax: float = 1046.50,  # C6
    min_note_seconds: float = 0.05,
    energy_gate: float = 0.006,
    bridge_unvoiced_seconds: float = 0.22,
    pitch_tolerance_semitones: int = 2,
) -> list[tuple[int, float, float]]:
    if audio.size == 0:
        return []

    y = audio.astype(np.float32)
    peak = float(np.max(np.abs(y)))
    if peak > 0:
        y = y / peak

    voiced_prob = None
    try:
        f0, _voiced_flag, voiced_prob = librosa.pyin(
            y,
            fmin=fmin,
            fmax=fmax,
            sr=sample_rate,
            frame_length=frame_length,
            hop_length=hop_length,
        )
    except Exception:
        f0 = librosa.yin(
            y,
            fmin=fmin,
            fmax=fmax,
            sr=sample_rate,
            frame_length=frame_length,
            hop_length=hop_length,
        )
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length).reshape(-1)

    if len(rms) < len(f0):
        rms = np.pad(rms, (0, len(f0) - len(rms)), mode="edge")
    elif len(rms) > len(f0):
        rms = rms[: len(f0)]

    active_rms = rms[rms > 0]
    effective_gate = float(energy_gate)
    if active_rms.size:
        adaptive_gate = max(0.0015, float(np.percentile(active_rms, 25)) * 0.35)
        effective_gate = min(effective_gate, adaptive_gate)

    voiced = np.isfinite(f0) & (rms >= effective_gate)
    if voiced_prob is not None:
        if len(voiced_prob) < len(f0):
            voiced_prob = np.pad(voiced_prob, (0, len(f0) - len(voiced_prob)), mode="edge")
        elif len(voiced_prob) > len(f0):
            voiced_prob = voiced_prob[: len(f0)]
        voiced_prob = np.nan_to_num(voiced_prob, nan=0.0)
        voiced &= voiced_prob >= 0.03
    notes = np.full(len(f0), -1, dtype=np.int16)
    if np.any(voiced):
        midi_vals = librosa.hz_to_midi(f0[voiced])
        notes[voiced] = np.rint(midi_vals).astype(np.int16)
    notes = np.clip(notes, -1, 127)

    if len(notes) > 4:
        smoothed_notes = notes.copy()
        for i in range(len(notes)):
            left = max(0, i - 2)
            right = min(len(notes), i + 3)
            window = notes[left:right]
            voiced_window = window[window >= 0]
            if voiced_window.size >= 2:
                smoothed_notes[i] = int(np.rint(np.median(voiced_window)))
        notes = smoothed_notes

    max_gap_frames = max(
        1,
        int(round((bridge_unvoiced_seconds * sample_rate) / hop_length)),
    )
    if len(notes) > 2 and max_gap_frames > 0:
        gap_start: int | None = None
        for i, note in enumerate(notes):
            note_int = int(note)
            if note_int < 0:
                if gap_start is None:
                    gap_start = i
                continue
            if gap_start is None:
                continue

            left_idx = gap_start - 1
            gap_len = i - gap_start
            if left_idx >= 0 and gap_len <= max_gap_frames:
                left_note = int(notes[left_idx])
                right_note = note_int
                if (
                    left_note >= 0
                    and right_note >= 0
                    and abs(left_note - right_note) <= pitch_tolerance_semitones
                ):
                    fill_note = int(round((left_note + right_note) / 2))
                    notes[gap_start:i] = fill_note
            gap_start = None

        for i in range(1, len(notes) - 1):
            left_note = int(notes[i - 1])
            this_note = int(notes[i])
            right_note = int(notes[i + 1])
            if left_note < 0 or this_note < 0 or right_note < 0:
                continue
            if (
                abs(left_note - right_note) <= pitch_tolerance_semitones
                and abs(this_note - left_note) > pitch_tolerance_semitones
                and abs(this_note - right_note) > pitch_tolerance_semitones
            ):
                notes[i] = int(round((left_note + right_note) / 2))

    events: list[tuple[int, float, float]] = []
    current_note: int | None = None
    start_idx = 0

    for i, note in enumerate(notes):
        note_int = int(note)
        if note_int < 0:
            if current_note is not None:
                start_sec = (start_idx * hop_length) / sample_rate
                end_sec = (i * hop_length) / sample_rate
                if end_sec - start_sec >= min_note_seconds:
                    events.append((current_note, start_sec, end_sec))
                current_note = None
            continue

        if current_note is None:
            current_note = note_int
            start_idx = i
            continue

        if abs(note_int - current_note) > pitch_tolerance_semitones:
            start_sec = (start_idx * hop_length) / sample_rate
            end_sec = (i * hop_length) / sample_rate
            if end_sec - start_sec >= min_note_seconds:
                events.append((current_note, start_sec, end_sec))
            current_note = note_int
            start_idx = i

    if current_note is not None:
        start_sec = (start_idx * hop_length) / sample_rate
        end_sec = (len(notes) * hop_length) / sample_rate
        if end_sec - start_sec >= min_note_seconds:
            events.append((current_note, start_sec, end_sec))

    if not events:
        return events

    merged_events: list[tuple[int, float, float]] = [events[0]]
    for note, start_sec, end_sec in events[1:]:
        last_note, last_start, last_end = merged_events[-1]
        gap_seconds = max(0.0, start_sec - last_end)
        if (
            gap_seconds <= bridge_unvoiced_seconds
            and abs(note - last_note) <= pitch_tolerance_semitones
        ):
            merged_events[-1] = (last_note, last_start, end_sec)
            continue
        merged_events.append((note, start_sec, end_sec))

    return merged_events


def write_midi(events: list[tuple[int, float, float]], out_path: Path, bpm: int = 120) -> None:
    midi = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    midi.tracks.append(track)

    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

    current_tick = 0
    for note, start_sec, end_sec in events:
        start_tick = int(mido.second2tick(start_sec, midi.ticks_per_beat, tempo))
        end_tick = int(mido.second2tick(end_sec, midi.ticks_per_beat, tempo))
        end_tick = max(end_tick, start_tick + 1)

        delta_on = max(0, start_tick - current_tick)
        track.append(mido.Message("note_on", note=int(note), velocity=96, time=delta_on))
        current_tick = start_tick

        delta_off = max(1, end_tick - current_tick)
        track.append(mido.Message("note_off", note=int(note), velocity=0, time=delta_off))
        current_tick = end_tick

    track.append(mido.MetaMessage("end_of_track", time=1))
    midi.save(str(out_path))


class Recorder:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.channels = 1
        self.stream: sd.InputStream | None = None
        self.frames: list[np.ndarray] = []
        self.level_history: list[tuple[float, float]] = []
        self.lock = threading.Lock()
        self.is_recording = False
        self.is_paused = False
        self.sample_count = 0

    def _callback(self, indata, _frames, _time, _status):
        with self.lock:
            if not self.is_recording or self.is_paused:
                return
            chunk = np.copy(indata[:, 0])  # mono
            self.frames.append(chunk)
            rms = float(np.sqrt(np.mean(chunk * chunk)))
            current_time = self.sample_count / float(self.sample_rate)
            midpoint_time = current_time + (chunk.shape[0] / (2.0 * self.sample_rate))
            self.level_history.append((midpoint_time, rms))
            self.sample_count += int(chunk.shape[0])

            cutoff_time = (self.sample_count / float(self.sample_rate)) - 15.0
            while self.level_history and self.level_history[0][0] < cutoff_time:
                self.level_history.pop(0)

    def start_new(self):
        with self.lock:
            self.frames = []
            self.level_history = []
            self.sample_count = 0
            self.is_recording = True
            self.is_paused = False
        self._ensure_stream_started()

    def pause(self):
        with self.lock:
            if self.is_recording:
                self.is_paused = True

    def resume(self):
        with self.lock:
            if self.is_recording:
                self.is_paused = False
        self._ensure_stream_started()

    def stop(self):
        with self.lock:
            self.is_recording = False
            self.is_paused = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None

    def _ensure_stream_started(self):
        if self.stream is not None and self.stream.active:
            return
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()

    def get_audio(self) -> np.ndarray:
        with self.lock:
            if not self.frames:
                return np.array([], dtype=np.float32)
            return np.concatenate(self.frames).astype(np.float32)

    def seconds_recorded(self) -> float:
        with self.lock:
            return self.sample_count / float(self.sample_rate)

    def status_snapshot(self) -> tuple[bool, bool, float]:
        with self.lock:
            seconds = self.sample_count / float(self.sample_rate)
            return self.is_recording, self.is_paused, seconds

    def get_recent_audio(self, seconds: float) -> np.ndarray:
        if seconds <= 0:
            return np.array([], dtype=np.float32)

        with self.lock:
            if not self.frames:
                return np.array([], dtype=np.float32)

            needed_samples = int(seconds * self.sample_rate)
            if needed_samples <= 0:
                return np.array([], dtype=np.float32)

            chunks: list[np.ndarray] = []
            remaining = needed_samples
            for frame in reversed(self.frames):
                frame_len = int(frame.shape[0])
                if frame_len <= remaining:
                    chunks.append(frame)
                    remaining -= frame_len
                else:
                    chunks.append(frame[-remaining:])
                    remaining = 0
                if remaining <= 0:
                    break

            if not chunks:
                return np.array([], dtype=np.float32)

            chunks.reverse()
            return np.concatenate(chunks).astype(np.float32)

    def get_level_history(self, seconds: float) -> list[tuple[float, float]]:
        with self.lock:
            if not self.level_history:
                return []
            if seconds <= 0:
                return list(self.level_history)

            cutoff_time = (self.sample_count / float(self.sample_rate)) - seconds
            return [(t, level) for (t, level) in self.level_history if t >= cutoff_time]


class MicToMidiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mic To MIDI Recorder")
        self.geometry("760x460")
        self.minsize(700, 420)

        self.recorder = Recorder(sample_rate=44100)
        self.last_saved_wav: Path | None = None
        self.visual_window_seconds = 8.0
        self.live_note_points: list[tuple[float, int]] = []
        self._build_ui()
        self._schedule_status_refresh()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        title = ttk.Label(
            root,
            text="Record from microphone and export to MIDI",
            font=("Segoe UI", 12, "bold"),
        )
        title.pack(anchor="w", pady=(0, 8))

        controls = ttk.Frame(root)
        controls.pack(fill="x")

        ttk.Button(controls, text="Start New", command=self.start_recording).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Pause", command=self.pause_recording).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Resume", command=self.resume_recording).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Stop", command=self.stop_recording).pack(
            side="left", padx=(0, 6)
        )

        ttk.Separator(root).pack(fill="x", pady=10)

        export_controls = ttk.Frame(root)
        export_controls.pack(fill="x")

        ttk.Button(export_controls, text="Save WAV", command=self.save_wav).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(export_controls, text="Export MIDI", command=self.export_midi).pack(
            side="left", padx=(0, 6)
        )

        bpm_wrap = ttk.Frame(export_controls)
        bpm_wrap.pack(side="left", padx=(8, 0))
        ttk.Label(bpm_wrap, text="MIDI BPM:").pack(side="left")
        self.bpm_var = tk.StringVar(value="120")
        ttk.Entry(bpm_wrap, width=6, textvariable=self.bpm_var).pack(side="left", padx=(4, 0))

        status_wrap = ttk.Frame(root)
        status_wrap.pack(fill="x", pady=(12, 8))

        self.state_var = tk.StringVar(value="State: idle")
        ttk.Label(status_wrap, textvariable=self.state_var).pack(side="left")

        self.time_var = tk.StringVar(value="Recorded: 0.00 sec")
        ttk.Label(status_wrap, textvariable=self.time_var).pack(side="right")

        viz_wrap = ttk.LabelFrame(root, text="Live Visualizer")
        viz_wrap.pack(fill="both", pady=(2, 10))

        self.viz_canvas = tk.Canvas(
            viz_wrap,
            height=185,
            bg="#0f131b",
            highlightthickness=1,
            highlightbackground="#273244",
        )
        self.viz_canvas.pack(fill="both", expand=True)
        self.viz_canvas.bind("<Configure>", lambda _event: self._draw_visualizer())

        self.log = tk.Text(root, height=10, wrap="word")
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

        hint = (
            "Tips:\n"
            "- Sing or hum one melody line for best MIDI results.\n"
            "- Avoid noisy background audio.\n"
            "- Live visualizer shows mic level (top) and detected MIDI preview (bottom).\n"
            "- Use Stop before Save WAV or Export MIDI."
        )
        self._log(hint)

    def _schedule_status_refresh(self):
        self.time_var.set(f"Recorded: {self.recorder.seconds_recorded():.2f} sec")
        self._update_visualizer_state()
        self.after(120, self._schedule_status_refresh)

    def _update_visualizer_state(self):
        is_recording, is_paused, elapsed = self.recorder.status_snapshot()
        if is_recording and not is_paused:
            preview_audio = self.recorder.get_recent_audio(0.42)
            detected_note = self._detect_live_note(preview_audio)
            if detected_note is None:
                self.live_note_points.append((elapsed, -1))
            else:
                self.live_note_points.append((elapsed, detected_note))
        elif self.live_note_points and self.live_note_points[-1][1] != -1:
            self.live_note_points.append((elapsed, -1))

        cutoff_time = elapsed - self.visual_window_seconds - 1.0
        while self.live_note_points and self.live_note_points[0][0] < cutoff_time:
            self.live_note_points.pop(0)

        self._draw_visualizer()

    def _detect_live_note(self, audio: np.ndarray) -> int | None:
        if audio.size < 1024:
            return None

        rms = float(np.sqrt(np.mean(audio * audio)))
        if rms < 0.006:
            return None

        voiced_prob = None
        try:
            f0, _voiced_flag, voiced_prob = librosa.pyin(
                audio.astype(np.float32),
                fmin=65.41,
                fmax=1046.50,
                sr=self.recorder.sample_rate,
                frame_length=1024,
                hop_length=128,
            )
        except Exception:
            try:
                f0 = librosa.yin(
                    audio.astype(np.float32),
                    fmin=65.41,
                    fmax=1046.50,
                    sr=self.recorder.sample_rate,
                    frame_length=1024,
                    hop_length=128,
                )
            except Exception:
                return None

        finite_f0 = f0[np.isfinite(f0)]
        if finite_f0.size == 0:
            return None

        if voiced_prob is not None:
            voiced_prob = np.nan_to_num(voiced_prob, nan=0.0)
            finite_prob = voiced_prob[np.isfinite(f0)]
            if finite_prob.size and float(np.median(finite_prob)) < 0.02:
                return None

        midi_vals = librosa.hz_to_midi(finite_f0)
        median_note = float(np.median(midi_vals))
        jitter = float(np.std(midi_vals))
        if jitter > 2.4:
            return None

        return int(np.clip(np.rint(median_note), 0, 127))

    def _note_to_y(self, note: int, y_top: float, y_bottom: float) -> float:
        min_note = 36
        max_note = 84
        span = max_note - min_note
        clipped = min(max(note, min_note), max_note)
        ratio = (clipped - min_note) / span if span > 0 else 0.0
        return y_bottom - ratio * (y_bottom - y_top)

    def _time_to_x(self, timestamp: float, start_time: float, width: int, pad_x: int) -> float:
        timeline = self.visual_window_seconds
        if timeline <= 0:
            return float(pad_x)
        ratio = (timestamp - start_time) / timeline
        ratio = max(0.0, min(1.0, ratio))
        return pad_x + ratio * max(1, width - (2 * pad_x))

    def _draw_visualizer(self):
        if not hasattr(self, "viz_canvas"):
            return

        canvas = self.viz_canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 20 or height < 20:
            return

        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill="#0f131b", outline="")

        pad_x = 12
        split_y = int(height * 0.55)
        top_y0 = 8
        top_y1 = max(top_y0 + 16, split_y - 8)
        midi_y0 = split_y + 8
        midi_y1 = height - 10

        canvas.create_line(0, split_y, width, split_y, fill="#2a3446", width=1)
        canvas.create_text(
            pad_x,
            top_y0,
            text="MIC LEVEL",
            anchor="nw",
            fill="#7ca4d6",
            font=("Segoe UI", 8, "bold"),
        )
        canvas.create_text(
            pad_x,
            midi_y0,
            text="MIDI PREVIEW",
            anchor="nw",
            fill="#f7b34a",
            font=("Segoe UI", 8, "bold"),
        )

        _, _, elapsed = self.recorder.status_snapshot()
        start_time = max(0.0, elapsed - self.visual_window_seconds)

        level_history = self.recorder.get_level_history(self.visual_window_seconds + 0.2)
        if level_history:
            level_points: list[float] = []
            usable_height = max(1.0, top_y1 - top_y0 - 8)
            for timestamp, level in level_history:
                if timestamp < start_time:
                    continue
                x = self._time_to_x(timestamp, start_time, width, pad_x)
                amplified = min(1.0, np.sqrt(max(level, 0.0) / 0.12))
                y = top_y1 - (amplified * usable_height)
                level_points.extend((x, y))
            if len(level_points) >= 4:
                canvas.create_line(level_points, fill="#52d1ff", width=2, smooth=True)

        for note in (36, 48, 60, 72, 84):
            y = self._note_to_y(note, midi_y0 + 12, midi_y1)
            line_color = "#3b4760" if note != 60 else "#4d6284"
            canvas.create_line(pad_x, y, width - pad_x, y, fill=line_color, dash=(2, 3))
            canvas.create_text(
                pad_x + 2,
                y - 2,
                text=f"{note}",
                anchor="sw",
                fill="#6c7f9e",
                font=("Segoe UI", 7),
            )

        note_points = [p for p in self.live_note_points if p[0] >= start_time - 0.5]
        if note_points:
            if note_points[0][0] > start_time:
                note_points.insert(0, (start_time, note_points[0][1]))

            prev_t, prev_note = note_points[0]
            for t, note in note_points[1:]:
                seg_start = max(prev_t, start_time)
                seg_end = min(t, elapsed)
                if prev_note >= 0 and seg_end > seg_start:
                    x0 = self._time_to_x(seg_start, start_time, width, pad_x)
                    x1 = self._time_to_x(seg_end, start_time, width, pad_x)
                    y = self._note_to_y(prev_note, midi_y0 + 12, midi_y1)
                    canvas.create_rectangle(
                        x0,
                        y - 3,
                        max(x0 + 1, x1),
                        y + 3,
                        fill="#f8b84e",
                        outline="",
                    )
                prev_t, prev_note = t, note

            seg_start = max(prev_t, start_time)
            if prev_note >= 0 and elapsed > seg_start:
                x0 = self._time_to_x(seg_start, start_time, width, pad_x)
                x1 = self._time_to_x(elapsed, start_time, width, pad_x)
                y = self._note_to_y(prev_note, midi_y0 + 12, midi_y1)
                canvas.create_rectangle(
                    x0,
                    y - 3,
                    max(x0 + 1, x1),
                    y + 3,
                    fill="#f8b84e",
                    outline="",
                )

        latest_note = None
        for timestamp, note in reversed(self.live_note_points):
            if elapsed - timestamp > 0.6:
                break
            if note >= 0:
                latest_note = note
                break
        if latest_note is None:
            note_text = "Live note: --"
        else:
            note_text = f"Live note: {latest_note}"

        canvas.create_text(
            width - pad_x,
            midi_y0 + 2,
            text=note_text,
            anchor="ne",
            fill="#f8b84e",
            font=("Segoe UI", 8, "bold"),
        )

    def _set_state(self, text: str):
        self.state_var.set(f"State: {text}")

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_recording(self):
        try:
            self.live_note_points = []
            self.recorder.start_new()
            self._set_state("recording")
            self._log("Started new recording.")
        except Exception as exc:
            messagebox.showerror("Recording error", str(exc))

    def pause_recording(self):
        self.recorder.pause()
        self._set_state("paused")
        self._log("Recording paused.")

    def resume_recording(self):
        try:
            self.recorder.resume()
            self._set_state("recording")
            self._log("Recording resumed.")
        except Exception as exc:
            messagebox.showerror("Recording error", str(exc))

    def stop_recording(self):
        self.recorder.stop()
        self._set_state("stopped")
        self._log("Recording stopped.")

    def _get_audio_or_warn(self) -> np.ndarray | None:
        audio = self.recorder.get_audio()
        if audio.size == 0:
            messagebox.showwarning("No audio", "No recorded audio found.")
            return None
        return audio

    def save_wav(self):
        audio = self._get_audio_or_warn()
        if audio is None:
            return
        out = filedialog.asksaveasfilename(
            title="Save recording as WAV",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
        )
        if not out:
            return
        out_path = Path(out)
        try:
            sf.write(str(out_path), audio, self.recorder.sample_rate)
            self.last_saved_wav = out_path
            self._log(f"Saved WAV: {out_path}")
        except Exception as exc:
            messagebox.showerror("Save WAV failed", str(exc))

    def export_midi(self):
        audio = self._get_audio_or_warn()
        if audio is None:
            return
        out = filedialog.asksaveasfilename(
            title="Export MIDI file",
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid")],
        )
        if not out:
            return

        try:
            bpm = int(self.bpm_var.get().strip())
            if bpm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid BPM", "BPM must be a positive integer.")
            return

        out_path = Path(out)
        self._set_state("converting to midi")
        self._log("Converting audio to MIDI...")

        thread = threading.Thread(
            target=self._export_midi_worker,
            args=(audio, out_path, bpm),
            daemon=True,
        )
        thread.start()

    def _export_midi_worker(self, audio: np.ndarray, out_path: Path, bpm: int):
        try:
            events = audio_to_note_events(
                audio,
                self.recorder.sample_rate,
                min_note_seconds=0.035,
                energy_gate=0.0045,
                bridge_unvoiced_seconds=0.28,
                pitch_tolerance_semitones=2,
            )
            if not events:
                self.after(
                    0,
                    lambda: messagebox.showwarning(
                        "No notes found",
                        "Could not detect stable notes. Try cleaner singing/humming.",
                    ),
                )
                self.after(0, lambda: self._set_state("stopped"))
                return

            audio_seconds = len(audio) / float(self.recorder.sample_rate)
            captured_seconds = sum((end_sec - start_sec) for _, start_sec, end_sec in events)
            coverage_pct = 0.0
            if audio_seconds > 0:
                coverage_pct = (captured_seconds / audio_seconds) * 100.0

            write_midi(events, out_path, bpm=bpm)
            self.after(
                0,
                lambda: self._log(
                    f"Saved MIDI: {out_path} ({len(events)} notes, {coverage_pct:.1f}% voiced coverage)"
                ),
            )
            self.after(0, lambda: self._set_state("stopped"))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Export MIDI failed", str(exc)))
            self.after(0, lambda: self._set_state("stopped"))


if __name__ == "__main__":
    app = MicToMidiApp()
    app.mainloop()
