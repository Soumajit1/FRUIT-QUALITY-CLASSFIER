import os
from PIL import Image, ImageDraw, ImageFont

def create_figure1():
    # Width x Height: 1200 x 650
    img = Image.new('RGB', (1200, 650), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_box_title = ImageFont.truetype("arialbd.ttf", 18)
        font_box_text = ImageFont.truetype("arial.ttf", 14)
        font_label = ImageFont.truetype("arialbd.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_box_title = ImageFont.load_default()
        font_box_text = ImageFont.load_default()
        font_label = ImageFont.load_default()

    # Draw Title
    draw.text((600, 30), "Figure 1: Dual-Engine System Architecture", fill=(30, 41, 59), font=font_title, anchor="mm")
    draw.line([(150, 55), (1050, 55)], fill=(203, 213, 225), width=2)

    def draw_box(xy, title, lines, fill_col, border_col, title_col=(15, 23, 42)):
        draw.rounded_rectangle(xy, radius=10, fill=fill_col, outline=border_col, width=2)
        cx = (xy[0] + xy[2]) // 2
        top_y = xy[1] + 16
        draw.text((cx, top_y), title, fill=title_col, font=font_box_title, anchor="mm")
        y = top_y + 24
        for line in lines:
            draw.text((cx, y), line, fill=(71, 85, 105), font=font_box_text, anchor="mm")
            y += 20

    # 1. Ingestion Box (Left)
    draw_box((60, 240, 260, 390), "User Ingestion", [
        "Image Upload (.jpg, .png)",
        "Live Camera Capture",
        "RGB Preprocessing (PIL)"
    ], (241, 245, 249), (148, 163, 184))

    # 2. Web UI / Controller Box (Middle-Left)
    draw_box((330, 220, 560, 410), "Streamlit App Engine", [
        "Web Presentation Layer",
        "Classic Responsive UI",
        "API Key & State Router",
        "Automatic Failover Logic"
    ], (238, 242, 255), (165, 180, 252), (67, 56, 202))

    # 3. Cloud Engine Box (Top-Right)
    draw_box((650, 110, 930, 260), "Cloud Multimodal LLM", [
        "Google Gemini Vision API",
        "(gemini-flash-lite-latest)",
        "Zero-Shot Variety Recognition",
        "Defect & Shelf-Life JSON"
    ], (240, 253, 244), (134, 239, 172), (22, 101, 52))

    # 4. Offline Fallback Box (Bottom-Right)
    draw_box((650, 360, 930, 510), "Offline Edge CNN Fallback", [
        "Local TensorFlow/Keras Model",
        "(fruit_quality_model.keras)",
        "224x224 RGB Tensor Input",
        "Softmax: Fresh vs. Rotten"
    ], (254, 242, 242), (252, 165, 165), (153, 27, 27))

    # 5. Persistent DB Box (Far-Right)
    draw_box((1000, 240, 1150, 390), "Storage & Logs", [
        "SQLite3 DB",
        "User Auth (SHA-256)",
        "Inspection Audit Log"
    ], (254, 249, 195), (250, 204, 21), (133, 77, 14))

    # Arrows
    # Ingestion -> Streamlit
    draw.line([(260, 315), (330, 315)], fill=(71, 85, 105), width=3)
    draw.polygon([(330, 315), (320, 310), (320, 320)], fill=(71, 85, 105))

    # Streamlit -> Cloud Gemini (Online)
    draw.line([(560, 280), (605, 280), (605, 185), (650, 185)], fill=(22, 101, 52), width=3)
    draw.polygon([(650, 185), (640, 180), (640, 190)], fill=(22, 101, 52))
    draw.text((605, 165), "Online (Primary)", fill=(22, 101, 52), font=font_label, anchor="mm")

    # Streamlit -> Local CNN (Offline Fallback)
    draw.line([(560, 350), (605, 350), (605, 435), (650, 435)], fill=(153, 27, 27), width=3)
    draw.polygon([(650, 435), (640, 430), (640, 440)], fill=(153, 27, 27))
    draw.text((605, 455), "Offline Fallback", fill=(153, 27, 27), font=font_label, anchor="mm")

    # Results -> Storage
    draw.line([(930, 185), (965, 185), (965, 315), (1000, 315)], fill=(71, 85, 105), width=2)
    draw.line([(930, 435), (965, 435), (965, 315)], fill=(71, 85, 105), width=2)
    draw.polygon([(1000, 315), (990, 310), (990, 320)], fill=(71, 85, 105))

    out_p1 = r"D:\DOWNLOADD\FruitQualityPro\FruitQualityPro\assets\figure1_system_architecture.png"
    out_p2 = r"D:\DOWNLOADD\figure1_system_architecture.png"
    img.save(out_p1)
    img.save(out_p2)
    print("Saved Figure 1 to:", out_p1, "and", out_p2)

def create_figure2():
    # Width x Height: 1200 x 650
    img = Image.new('RGB', (1200, 650), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_box_title = ImageFont.truetype("arialbd.ttf", 16)
        font_box_text = ImageFont.truetype("arial.ttf", 13)
        font_label = ImageFont.truetype("arialbd.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_box_title = ImageFont.load_default()
        font_box_text = ImageFont.load_default()
        font_label = ImageFont.load_default()

    # Draw Title
    draw.text((600, 30), "Figure 2: End-to-End Image Processing and Diagnostic Flowchart", fill=(30, 41, 59), font=font_title, anchor="mm")
    draw.line([(120, 55), (1080, 55)], fill=(203, 213, 225), width=2)

    def draw_rounded(xy, text_lines, fill_col, border_col, title_col=(15, 23, 42)):
        draw.rounded_rectangle(xy, radius=8, fill=fill_col, outline=border_col, width=2)
        cx = (xy[0] + xy[2]) // 2
        cy = (xy[1] + xy[2]) // 2 if len(text_lines) == 1 else xy[1] + 16
        if len(text_lines) == 1:
            draw.text((cx, cy), text_lines[0], fill=title_col, font=font_box_title, anchor="mm")
        else:
            draw.text((cx, cy), text_lines[0], fill=title_col, font=font_box_title, anchor="mm")
            y = cy + 22
            for line in text_lines[1:]:
                draw.text((cx, y), line, fill=(71, 85, 105), font=font_box_text, anchor="mm")
                y += 18

    # Steps from Left to Right
    # 1. Start / Input
    draw_rounded((40, 270, 190, 360), ["Input Image", "File Upload / Camera"], (241, 245, 249), (148, 163, 184))

    # 2. Preprocessing
    draw_rounded((240, 270, 410, 360), ["Preprocessing", "RGB conversion & validation"], (238, 242, 255), (165, 180, 252))

    # 3. Decision Diamond (Check Network & API Key)
    # Center at (530, 315), size 100x70
    pts = [(530, 255), (610, 315), (530, 375), (450, 315)]
    draw.polygon(pts, fill=(254, 249, 195), outline=(234, 179, 8))
    draw.text((530, 305), "Gemini API", fill=(133, 77, 14), font=font_box_title, anchor="mm")
    draw.text((530, 325), "Available?", fill=(133, 77, 14), font=font_box_text, anchor="mm")

    # 4A. Cloud Route (Top)
    draw_rounded((680, 150, 920, 240), ["Cloud Gemini Vision", "Extract Variety, Defects,", "Ripeness & Shelf Life (JSON)"], (240, 253, 244), (134, 239, 172), (22, 101, 52))

    # 4B. Offline Fallback Route (Bottom)
    draw_rounded((680, 390, 920, 480), ["Local Keras CNN", "Resize 224x224 Tensor", "Predict Fresh vs. Rotten"], (254, 242, 242), (252, 165, 165), (153, 27, 27))

    # 5. Output Card & DB Log
    draw_rounded((990, 270, 1160, 360), ["Display & Log", "Render Diagnostic Card", "Save to SQLite DB"], (243, 244, 246), (156, 163, 175))

    # Connecting Arrows
    # 1 -> 2
    draw.line([(190, 315), (240, 315)], fill=(71, 85, 105), width=3)
    draw.polygon([(240, 315), (230, 310), (230, 320)], fill=(71, 85, 105))

    # 2 -> 3
    draw.line([(410, 315), (450, 315)], fill=(71, 85, 105), width=3)
    draw.polygon([(450, 315), (440, 310), (440, 320)], fill=(71, 85, 105))

    # 3 -> 4A (Yes / Online)
    draw.line([(530, 255), (530, 195), (680, 195)], fill=(22, 101, 52), width=3)
    draw.polygon([(680, 195), (670, 190), (670, 200)], fill=(22, 101, 52))
    draw.text((570, 180), "Yes (Online)", fill=(22, 101, 52), font=font_label, anchor="mm")

    # 3 -> 4B (No / Offline)
    draw.line([(530, 375), (530, 435), (680, 435)], fill=(153, 27, 27), width=3)
    draw.polygon([(680, 435), (670, 430), (670, 440)], fill=(153, 27, 27))
    draw.text((570, 450), "No (Offline)", fill=(153, 27, 27), font=font_label, anchor="mm")

    # 4A & 4B -> 5
    draw.line([(920, 195), (955, 195), (955, 315), (990, 315)], fill=(71, 85, 105), width=3)
    draw.line([(920, 435), (955, 435), (955, 315)], fill=(71, 85, 105), width=3)
    draw.polygon([(990, 315), (980, 310), (980, 320)], fill=(71, 85, 105))

    out_p1 = r"D:\DOWNLOADD\FruitQualityPro\FruitQualityPro\assets\figure2_workflow_flowchart.png"
    out_p2 = r"D:\DOWNLOADD\figure2_workflow_flowchart.png"
    img.save(out_p1)
    img.save(out_p2)
    print("Saved Figure 2 to:", out_p1, "and", out_p2)

if __name__ == "__main__":
    create_figure1()
    create_figure2()
