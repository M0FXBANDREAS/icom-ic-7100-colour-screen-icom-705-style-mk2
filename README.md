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

# HamTec IC-7100 Photo Console

A Linux control panel for the **Raspberry Pi 4 and Icom IC-7100**, using a real IC-705 photograph with a live display over its LCD.

**Version:** 0.3  
**Target system:** Debian 13 ARM64 on Raspberry Pi 4  
**Connection:** USB CI-V and USB receive audio

This is an independent HamTec project, not official Icom software.

## Features

- Real IC-705 photograph bundled with the application.
- Black background and surround.
- Live frequency and operating-mode display.
- Draggable VFO tuning knob.
- Mouse-wheel and keyboard tuning.
- FIL1, FIL2 and FIL3 selection through CI-V.
- Direct frequency entry and band presets.
- Live received-audio spectrum and waterfall.
- Automatic sizing when the browser window changes.
- Size slider, drag-to-resize handle and FIT button.
- Radio view and screen-only view.
- Clickable photographed MENU, M.SCOPE, QUICK and EXIT buttons.
- No demo mode or simulated radio readings.

## Requirements

- Raspberry Pi 4 with a suitable power supply.
- Debian 13 ARM64 with a desktop environment.
- Chromium browser.
- Icom IC-7100 with its original control head connected.
- USB-A to mini-B data cable between the Pi and radio main unit.
- Monitor or touchscreen.
- Internet connection for dependency installation.

The radio requires its normal power supply.

## 1. Download and install

Download `HamTec-IC7100-Photo-Console.zip` into the Pi’s Downloads folder.

Stop any previous panel server using **Ctrl+C** in its terminal.

Open a terminal on the Pi and paste:

```bash
sudo apt update
sudo apt install -y unzip python3-venv libportaudio2

mkdir -p "$HOME/hamtec-photo"

unzip "$HOME/Downloads/HamTec-IC7100-Photo-Console.zip" \
  -d "$HOME/hamtec-photo"

cd "$HOME/hamtec-photo/ic7100-panel"

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

bash start-panel.sh
```

If the ZIP is saved elsewhere, change the download path.

Leave the terminal running.

Open Chromium on the Pi and visit:

**http://127.0.0.1:7100**

Refresh the page if an older version of the panel appears.

## 2. Start the panel later

After installation, use:

```bash
cd "$HOME/hamtec-photo/ic7100-panel"
bash start-panel.sh
```

Press **Ctrl+C** to stop the server.

## 3. IC-7100 USB connection

The application defaults to the CI-V interface detected on this setup:

```text
/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_IC-7100_03006987_A-if00-port0
```

The default CI-V settings are:

| Setting | Value |
| --- | --- |
| Baud rate | 19200 |
| Radio address | 88 hexadecimal |

Make sure the radio’s CI-V settings match.

To override the settings:

```bash
bash start-panel.sh --baud 19200 --address 88
```

The address argument is hexadecimal: `88` means `0x88`.

For a different radio serial device:

```bash
bash start-panel.sh \
  --port /dev/serial/by-id/YOUR_ICOM_CIV_DEVICE \
  --baud 19200 \
  --address 88
```

Find available serial devices with:

```bash
ls -l /dev/serial/by-id/
```

Keep the original IC-7100 control head connected. Close other applications using the same CI-V port.

If the USB serial device is disconnected and reconnected, restart the server.

### Serial permission errors

If access is denied:

```bash
sudo usermod -aG dialout "$USER"
```

Log out and back in, or reboot, before starting again.

Do not run the application as root.

## 4. VFO knob

The large photographed dial on the right controls receive frequency.

- Drag clockwise to tune up.
- Drag counter-clockwise to tune down.
- Scroll over the dial to tune.
- Scroll over the frequency display to tune.
- Use the on-screen + and − buttons.
- Use up/down arrow keys when no dialog or form control has focus.
- Use left/right arrow keys when the dial has keyboard focus.

Every six degrees of dial movement adds one tuning step.

Select the tuning step on the display:

- 10 Hz
- 100 Hz
- 1 kHz
- 10 kHz

The photographed **QUICK** button cycles the tuning step.

Dial animation responds immediately. Actual radio tuning depends on a successful CI-V command and radio readback.

## 5. Receive filters

Tap the blue **FIL** box to select:

- FIL1
- FIL2
- FIL3

The application sends the selected filter to the IC-7100 through CI-V and reads the selection back from the radio.

A filter-only change preserves the current operating mode.

The bandwidth of each preset comes from the settings stored on your IC-7100 for the current mode. The application does not assume or modify those bandwidths.

Unsupported selections are rejected by the radio and shown as errors.

## 6. Frequency, mode and bands

| Control | Action |
| --- | --- |
| Large frequency display | Enter receive frequency in MHz |
| Mode box | Select operating mode |
| MENU or BAND | Open band presets |
| + / − buttons | Tune by the selected step |
| QUICK hardware button | Cycle tuning step |

Band presets are receive starting points, not a transmit band-plan guide.

## 7. Live audio waterfall

On the IC-7100:

1. Set **ACC/USB Output Select** to **AF**.
2. Adjust the USB AF output level for a usable signal without clipping.

The server tries to select a uniquely matching Icom/USB audio input automatically.

If automatic selection fails, list the audio devices:

```bash
cd "$HOME/hamtec-photo/ic7100-panel"
.venv/bin/python -m sounddevice
```

Find the numeric input-device index for the radio.

Stop the server and restart with your actual device index. The following example uses `3`:

```bash
bash start-panel.sh --audio-device 3
```

The selected input must support mono capture at 48 kHz.

Audio-device indices can change after reconnecting USB or rebooting.

The waterfall displays **received audio frequencies**, not a wideband RF bandscope. This version processes AF audio, not the IC-7100’s 12 kHz IF output.

No simulated signals are substituted when audio is unavailable.

### Scope controls

| Control | Action |
| --- | --- |
| HOLD | Freeze waterfall history |
| CENT/FIX | Clear waterfall history |
| SPAN | Adjust displayed audio-frequency span |
| REF | Adjust display reference level |
| EXPD/SET | Expand the spectrum area |

Radio polling continues while waterfall history is held.

## 8. Resize the panel

The radio and controls resize together to retain their alignment.

- Resize the browser window for automatic fitting.
- Use the **SIZE** slider to enlarge or reduce the panel.
- Drag the lower-right resize handle.
- Click **FIT** to return to automatic fitting.

Views larger than the available window can scroll.

### Radio view

Shows the actual IC-705 photograph, live display and draggable VFO knob.

### Screen view

Shows the flat LCD without the photographed chassis.

Use **SCREEN VIEW / RADIO VIEW** to switch.

The large photographed dial is available only in radio view. Tuning buttons and keyboard controls remain available in screen view.

## 9. Photographed hardware buttons

| Button | Action |
| --- | --- |
| MENU | Open the menu |
| M.SCOPE | Expand or restore the scope |
| QUICK | Cycle tuning step |
| EXIT | Close an open dialog |

Other photographed controls are part of the image and are not implemented as radio controls.

## 10. Full-screen and kiosk mode

Choose **MENU → FULL SCREEN**.

Alternatively, leave the server running and open a second terminal on the Pi desktop:

```bash
chromium --kiosk http://127.0.0.1:7100
```

If your browser command is `chromium-browser`:

```bash
chromium-browser --kiosk http://127.0.0.1:7100
```

Press **Alt+F4** to close the kiosk window.

Automatic startup is not configured by this project.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Browser cannot connect | Keep the server running and open the URL on the Pi itself |
| Old interface appears | Refresh the browser; if necessary, use Ctrl+Shift+R |
| Address already in use | Stop the previous panel server |
| USB disconnected | Check radio power, cable and selected serial port |
| Permission denied | Add your user to `dialout`, then log out and back in |
| No CI-V reply | Check baud rate, address and competing radio applications |
| Dial moves but frequency does not | Check USB connection and CI-V errors under MENU → SET |
| Filter change rejected | Check whether the preset is supported in the current radio mode |
| No audio waterfall | Check AF output selection, output level and audio input |
| Automatic audio selection fails | Specify the input index using `--audio-device` |
| Audio capture fails | Select an input supporting mono 48 kHz |
| Panel is too large | Click FIT or reduce SIZE |
| Python module is missing | Install `requirements.txt` using the project virtual environment |

Connection and audio errors appear under **MENU → SET**.

To use another HTTP port:

```bash
bash start-panel.sh --http-port 7101
```

Then open:

**http://127.0.0.1:7101**

The server listens on the Pi’s local loopback address. It is not configured for access from another computer.

## Current limitations

The following are not implemented:

- Live S-meter measurement.
- AGC, preamp, attenuator and noise-reduction control.
- Arbitrary receive-filter bandwidth editing.
- VFO A/B selection.
- Wideband RF spectrum input.
- Speaker playback or remote audio streaming.
- Transmit/PTT controls.
- Automatic startup.

Unavailable radio readings remain blank or show an unavailable label.

**No tests, browser checks or hardware tests were run for this release, as requested.** The layout, resizing, VFO interaction and CI-V filter controls are implemented but remain unverified on the Pi and transceiver.

## Project files

| File | Purpose |
| --- | --- |
| `server.py` | Local web server, CI-V control and audio FFT |
| `start-panel.sh` | Launch using the virtual environment |
| `requirements.txt` | Python dependencies |
| `web/index.html` | Radio interface |
| `web/assets/ic705.png` | Bundled IC-705 photograph |
| `web/assets/ATTRIBUTION.md` | Photograph attribution and license details |

## Photograph attribution

Original photograph: **Batchman99**  
Derivative version: **VORON SPb**

Licensed under **Creative Commons Attribution-ShareAlike 4.0 International**.

The application uses CSS clipping, a live-screen overlay and a circular dial crop as adaptations of the photograph under the same license.

- [Photograph source](https://commons.wikimedia.org/wiki/File:ICOM_IC-705_nobg.png)
- [Original photograph](https://commons.wikimedia.org/wiki/File:ICOM_IC-705.jpg)
- [CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/)

No endorsement by Icom or the photographers is implied.

## References

- [Icom IC-7100 product page and manuals](https://www.icomjapan.com/lineup/products/IC-7100EUR/)
- [Icom IC-705 product page](https://www.icomjapan.com/lineup/products/IC-705/)

Filter selection follows the IC-7100 manual’s Control Command section: commands 04 and 06 carry operating mode and filter selection, with 01 for FIL1, 02 for FIL2 and 03 for FIL3.
