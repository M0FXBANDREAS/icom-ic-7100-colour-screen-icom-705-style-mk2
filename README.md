# HamTec IC-7100 · Photo Console v0.3

Raspberry Pi 4 / Debian 13 ARM64 / Icom IC-7100 USB.

This version uses a real photograph of the IC-705 as the radio chassis, with a live screen projected over the photographed LCD. The exterior and surrounding page are black. It is an independent HamTec control application, not official Icom software.

## New in this release

- Actual bundled IC-705 photograph, available offline after installation.
- Live LCD placed in perspective over the photograph.
- Photo-textured VFO knob: touch/mouse drag clockwise to tune up, counter-clockwise to tune down. Mouse wheel and arrow keys also tune.
- FIL1/FIL2/FIL3 selection sent to the IC-7100 through CI-V, preserving the current operating mode when changing only the filter.
- Filter readback from the radio; no invented bandwidth values.
- Relative tuning reads the radio frequency before applying dial movement. Dial movements are accumulated instead of discarded while another request is running.
- Automatic window fit, SIZE slider, FIT button and a draggable lower-right resizing handle. Larger-than-window views can scroll.
- RADIO VIEW / SCREEN VIEW switch, with the same live controls in both.
- Clickable photographed MENU, M.SCOPE, QUICK and EXIT keys. QUICK cycles the tuning step.
- Live USB received-audio waterfall; no demonstration mode or generated spectrum signals.

## Install this update

Download `HamTec-IC7100-Photo-Console.zip` into the Pi's Downloads folder. Stop the old server with Ctrl+C and install into a separate directory:

```bash
sudo apt update
sudo apt install -y unzip python3-venv libportaudio2
mkdir -p "$HOME/hamtec-photo"
unzip "$HOME/Downloads/HamTec-IC7100-Photo-Console.zip" -d "$HOME/hamtec-photo"
cd "$HOME/hamtec-photo/ic7100-panel"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
bash start-panel.sh
```

Open Chromium on the Pi at **http://127.0.0.1:7100**.

For later launches:

```bash
cd "$HOME/hamtec-photo/ic7100-panel"
bash start-panel.sh
```

The default serial device is your previously supplied interface:

```text
/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7100_03006987_A-if00-port0
```

The radio CI-V settings must match **19200 baud**, **address 88h**. Override if needed:

```bash
bash start-panel.sh --baud 19200 --address 88
```

Keep the original IC-7100 control head connected. Close other applications using the same serial port. If serial access is denied, run this, then log out and back in:

```bash
sudo usermod -aG dialout "$USER"
```

If USB is disconnected/reconnected, restart the server to reopen the serial port.

## VFO tuning

Drag around the large photographed dial on the right. Every six degrees adds a tuning step. Use the screen's step selector to choose 10 Hz, 100 Hz, 1 kHz or 10 kHz. The photographed QUICK key cycles the step.

Scroll over the dial or frequency display to tune. Up/down arrow keys tune when no dialog or form control is active; left/right arrows also tune when the dial has keyboard focus.

Dial animation is immediate. Actual tuning depends on the IC-7100 acknowledging the CI-V command. Connection errors are shown rather than pretending the radio changed frequency.

## Receive filters

Tap the blue FIL box to open FIL1/FIL2/FIL3. Selecting a preset changes the radio's receive filter using CI-V command 06 with its current mode and the chosen filter byte. Readback uses command 04.

Preset bandwidths come from the settings stored on your IC-7100 for the current mode. The application does not assume, label or modify their bandwidths. A radio-rejected selection appears as an error. DV and other mode restrictions are handled by the radio.

## Resize and views

The photograph and controls retain their alignment as the browser window changes size. Use SIZE to enlarge or reduce the radio, drag the lower-right triangle, or click FIT to return to automatic fitting.

SCREEN VIEW presents the flat LCD without the photographed chassis. RADIO VIEW restores the photograph and large VFO dial. The VFO dial is visible only in RADIO VIEW; tuning buttons and keyboard controls remain available in SCREEN VIEW.

MENU → FULL SCREEN toggles fullscreen. Alternatively, use a second Pi desktop terminal while the server runs:

```bash
chromium --kiosk http://127.0.0.1:7100
```

Some installations call the browser `chromium-browser`.

## Live audio waterfall

On the radio select **ACC/USB Output Select: AF** and adjust its AF output level. The server attempts to select a unique Icom/USB audio input automatically.

If automatic selection fails, list audio inputs:

```bash
cd "$HOME/hamtec-photo/ic7100-panel"
.venv/bin/python -m sounddevice
```

Stop the server and supply your actual capture-device index. Here, `3` is an example:

```bash
bash start-panel.sh --audio-device 3
```

The device must support mono input at 48 kHz. Audio errors appear in MENU → SET. Serial frequency/filter control remains available when audio is unavailable.

HOLD freezes waterfall history. SPAN and REF adjust the AF display, CENT/FIX clears history, and EXPD/SET enlarges the spectrum area.

## Limits

The waterfall displays received audio, not a wideband RF scope. USB audio from the IC-7100 does not provide the IC-705's native RF spectrum data. No simulated signals are substituted.

S-meter, AGC, P.AMP, ATT and NR readouts remain unavailable. There is no PTT, transmitter control, speaker playback, VFO A/B selection, arbitrary filter-bandwidth editing or automatic startup service.

**No tests, browser checks or hardware tests were run for this update, as requested.** Photo/control alignment, resizing, knob interaction and CI-V filter operation are implemented but unverified on your Pi and transceiver.

## Photograph credit

Photograph: Batchman99; derivative version: VORON SPb. Creative Commons Attribution-ShareAlike 4.0. CSS clipping, the live-screen overlay and dial crop are adaptations of the photo under the same license. Full credit and links: `web/assets/ATTRIBUTION.md`.

Source: https://commons.wikimedia.org/wiki/File:ICOM_IC-705_nobg.png
License: https://creativecommons.org/licenses/by-sa/4.0/

## Protocol reference

Icom IC-7100 full manual, Control Command section 20-11: commands 04 and 06 carry operating mode and filter selection (01=FIL1, 02=FIL2, 03=FIL3).

Official manual listing: https://www.icomjapan.com/lineup/products/IC-7100EUR/
