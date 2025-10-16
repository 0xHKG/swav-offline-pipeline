#!/bin/bash

# Monitor script for Swavlamban 2025 render progress

OUTPUT_DIR="/home/gogi/Desktop/Swavlamban 2025/swav_offline_pipeline/renders/swav2025/intermediate"

echo "========================================"
echo "SWAVLAMBAN 2025 RENDER PROGRESS MONITOR"
echo "========================================"
echo ""
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Count completed shots
SHOT_COUNT=$(ls -1 "$OUTPUT_DIR"/shot_*.mp4 2>/dev/null | wc -l)
echo "✓ Shots Completed: $SHOT_COUNT / 54"
echo ""

# Calculate progress percentage
PROGRESS=$((SHOT_COUNT * 100 / 54))
echo "Progress: $PROGRESS%"
echo ""

# Show file sizes
echo "Generated Shot Files:"
cd "$OUTPUT_DIR" && ls -lh shot_*.mp4 2>/dev/null | tail -5 | awk '{print "  " $9 " - " $5}'
echo ""

# Show latest shot being processed
cd "$OUTPUT_DIR"
LATEST_SHOT=$(ls -t shot_*.mp4 2>/dev/null | head -1)
if [ -n "$LATEST_SHOT" ]; then
    echo "Latest Completed: $LATEST_SHOT"
    echo "  Size: $(ls -lh "$LATEST_SHOT" | awk '{print $5}')"
    echo "  Modified: $(stat -c '%y' "$LATEST_SHOT" | cut -d'.' -f1)"
fi

echo ""
echo "========================================"
