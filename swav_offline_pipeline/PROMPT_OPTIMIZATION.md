# Prompt Optimization Guide for Swavlamban 2025

## Executive Summary

**Key Finding:** Current prompts contain film editing directions and text overlays that AI video models cannot render properly, resulting in garbled output and poor quality.

**Solution:** Separate visual descriptions from text overlays, add cinematic quality descriptors, and simplify prompts for better AI comprehension.

---

## Problems with Current Prompts

### 1. **Text in Prompts** (Major Issue)
**Problem:** AI models cannot generate readable text - they create garbled approximations

**Example - r001 Current:**
```
"Super: 'Swavlamban 2025 · Manekshaw Centre · 25–26 Nov 2025'"
```

**Result:** Garbled text like "SUMVWAlANRia Mealan 200± 2023)"

**Solution:** Remove ALL text from prompts. Add text as post-processing overlays using FFmpeg.

---

### 2. **Editing Directions Mixed with Visuals**
**Problem:** Terms like "fade", "cut to", "Super:", "swell" are post-production instructions, not visual descriptions

**Example - r001 Current:**
```
"Black to Indian Navy crest...; slow fade to...; crisp brass section swell."
```

**Issues:**
- "Black to" = transition instruction
- "slow fade" = editing effect
- "brass section swell" = audio, not visual

**Solution:** Describe only what should be VISIBLE on screen

---

### 3. **Multiple Subjects Per Prompt**
**Problem:** AI models struggle with multiple distinct subjects in one shot

**Example - r001 Current:**
```
"Indian Navy crest over the Tricolour; slow fade to the façade of Manekshaw Centre"
```

**Issues:**
- 3 subjects: Navy crest, flag, building
- AI gets confused, generates artifacts

**Solution:** One primary subject per shot. Simplify.

---

### 4. **Missing Quality/Style Descriptors**
**Problem:** No guidance on cinematography, lighting, or realism level

**Current prompts lack:**
- Lighting direction (golden hour, studio, natural)
- Camera movement (static, dolly, crane)
- Style keywords (photorealistic, cinematic, professional)
- Quality boosters (4K, sharp focus, detailed)

---

## Prompt Optimization Formula

### **Structure:**
```
[Subject] + [Action/State] + [Environment] + [Camera] + [Lighting] + [Style] + [Quality]
```

### **Best Practices for HunyuanVideo:**

1. **Be Specific & Visual**
   - Good: "The Indian tricolor flag waving gently in the breeze against a clear blue sky"
   - Bad: "Flag"

2. **Add Cinematic Keywords**
   - "cinematic establishing shot"
   - "professional corporate documentary style"
   - "photorealistic 4K footage"
   - "sharp focus, high detail"

3. **Specify Camera Work**
   - "static wide shot"
   - "slow camera push-in"
   - "aerial drone footage"
   - "handheld documentary style"

4. **Describe Lighting**
   - "golden hour sunlight"
   - "professional studio lighting"
   - "natural daylight, bright and clear"
   - "dramatic side lighting"

5. **Keep It Focused**
   - One primary subject per shot
   - 20-40 words maximum
   - No text, no transitions, no audio cues

---

## Optimized Prompts - First 5 Shots

### **r001 - Opening Shot**

**ORIGINAL (Problematic):**
```
Black to Indian Navy crest over the Tricolour; slow fade to the façade
of Manekshaw Centre; crisp brass section swell. Super: "Swavlamban 2025
· Manekshaw Centre · 25–26 Nov 2025".
```

**OPTIMIZED (Video-only):**
```
Cinematic establishing shot of Manekshaw Centre exterior in New Delhi,
grand colonial architecture building with beige stone facade and arched
windows, Indian tricolor flag waving on flagpole in foreground, golden
hour lighting, photorealistic 4K, professional documentary style, static
wide shot, sharp focus
```

**Post-Production:** Add text overlay in FFmpeg:
- "SWAVLAMBAN 2025"
- "Manekshaw Centre · 25-26 Nov 2025"
- "नवाचार एवं स्वदेशीकरण से सशक्तिकरण"

---

### **r002 - Corridor Walk**

**ORIGINAL:**
```
A dignified corridor walk-through: officers and sailors pass framed
photographs of ships, submarines and fleet exercises; exhibition
signage reveals the floor plan; ushers guide visitors.
```

**OPTIMIZED:**
```
Wide corridor shot in professional exhibition hall, Indian Navy officers
in white uniforms walking past wall-mounted photographs of warships and
submarines, modern corporate interior with polished marble floors, soft
overhead lighting, cinematic tracking shot, photorealistic, documentary
style, 4K quality, professional framing
```

---

### **r003 - Naval Operations Montage**

**ORIGINAL:**
```
Montage: INS Vikrant under way; frigate at speed; a submarine slipping
beneath the surface; carrier deck operations; a destroyer launching a
missile; cut to labs and integration bays.
```

**ISSUE:** Too many subjects for one shot!

**OPTIMIZED (Split into focused shots):**

**Option A - Aircraft Carrier:**
```
Cinematic aerial shot of INS Vikrant aircraft carrier cutting through
blue ocean waters, massive grey naval vessel with flight deck, creating
white wake, dramatic side lighting, photorealistic maritime footage,
4K quality, professional naval documentary style, stable drone shot
```

**Option B - Submarine:**
```
Submarine slowly submerging beneath ocean surface, grey hull breaking
through blue-green water, creating ripples and foam, golden hour
lighting, cinematic wide shot, photorealistic military footage, 4K
detail, professional documentary style, dramatic low angle
```

---

### **r004 - NIIO Welcome**

**ORIGINAL:**
```
NIIO welcome desk; inaugural lamp-lighting; the exhibition opens;
the hall is ordered, calm, professional.
```

**OPTIMIZED:**
```
Modern exhibition welcome desk with professional staff in Indian Navy
uniforms, clean corporate interior with navy branding, visitors
registering at counter, bright natural lighting from large windows,
cinematic medium shot, photorealistic 4K, professional corporate event
style, steady camera, sharp focus
```

---

### **r005 - Statistics Display**

**ORIGINAL:**
```
Minimal onscreen counter animates once and settles; no flashy motion graphics.
```

**ISSUE:** This is purely graphic design - AI can't generate text/numbers

**OPTIMIZED APPROACH:**
- **Video:** Simple abstract background (navy blue gradient, subtle motion)
- **Graphics:** Create counter animation in After Effects or similar
- **Composite:** Overlay graphics on video background

**Video Prompt:**
```
Abstract dark navy blue gradient background with subtle slow diagonal
light rays moving across frame, professional corporate style, cinematic
4K quality, smooth motion, clean and minimal aesthetic, studio lighting
```

---

## Implementation Strategy

### **Phase 1: Automated Enhancement (Recommended)**

Create a prompt enhancement function in the renderer:

```python
def enhance_prompt(original_prompt, shot_id):
    """Add quality and style keywords to existing prompts"""

    # Quality boosters
    quality = "photorealistic 4K footage, sharp focus, high detail, professional grade"

    # Style boosters based on shot type
    if "naval" in original_prompt.lower() or "ship" in original_prompt.lower():
        style = "cinematic naval documentary style, dramatic ocean lighting"
    elif "exhibition" in original_prompt.lower() or "hall" in original_prompt.lower():
        style = "professional corporate event cinematography, clean framing"
    elif "officer" in original_prompt.lower() or "sailor" in original_prompt.lower():
        style = "respectful military documentary style, dignified presentation"
    else:
        style = "cinematic documentary style, professional composition"

    # Camera work (default to stable shots for formal content)
    camera = "static wide shot" if not "walk" in original_prompt.lower() else "smooth tracking shot"

    # Combine
    enhanced = f"{original_prompt}, {camera}, {style}, {quality}"

    return enhanced
```

### **Phase 2: Manual Optimization (Best Quality)**

Create `storyboard.swav2025v2_optimized.yaml` with hand-crafted prompts for all 54 shots.

**Benefits:**
- Maximum control over output
- Tailored to each shot's specific needs
- Can split complex shots into simpler ones

**Effort:** ~2-3 hours to rewrite 54 prompts

---

## Text Overlay Post-Processing

Since AI cannot generate readable text, add overlays using FFmpeg:

```bash
ffmpeg -i input.mp4 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='SWAVLAMBAN 2025':\
x=(w-text_w)/2:y=50:\
fontsize=48:\
fontcolor=white:\
borderw=2:\
bordercolor=black" \
  -c:a copy output.mp4
```

**Advantages:**
- Clean, professional text
- Easily editable
- Multiple languages (Hindi + English)
- Consistent branding

---

## Audio Prompts (TTS Optimization)

Current narration prompts are excellent - they're already conversational and context-rich.

**Minor Enhancement:** Add SSML tags for Chatterbox/F5-TTS if switching from XTTS:

```xml
<speak>
  <prosody rate="slow" pitch="low">
    Swavlamban 2025—the Indian Navy's annual seminar and exhibition
    of innovation and indigenisation, organised by the Naval Innovation
    & Indigenisation Organisation, NIIO.
  </prosody>
</speak>
```

**Keywords for better TTS:**
- `rate="slow"` for ceremonial tone
- `pitch="low"` for authority
- `<break time="500ms"/>` for dramatic pauses

---

## Recommendation

**For immediate test:** Use automated enhancement function (Phase 1)
- Quick implementation (~30 min coding)
- Consistent quality boost across all shots
- Reversible if needed

**For production render:** Create optimized YAML (Phase 2) after seeing Phase 1 results
- Higher quality potential
- More control
- Worth the effort for 54-shot exhibition film

---

## Next Steps

1. **Test with r001:** Render with enhanced prompt using HunyuanVideo
2. **Compare quality:** Enhanced vs. original prompt
3. **If better:** Apply enhancement function to all 54 shots
4. **Add text overlays:** Post-process with FFmpeg
5. **Final render:** Full 54-shot production with optimized prompts

---

**Expected Improvement:** 30-50% quality boost from prompt optimization alone, plus elimination of garbled text artifacts.
