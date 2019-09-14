import cv2

def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness, cv2.LINE_AA)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness, cv2.LINE_AA)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness, cv2.LINE_AA)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness, cv2.LINE_AA)

def draw_text_w_background(img, text, coords, font, fontScale, fontColor, bgColor, thickness):
	lines = text.split("\n")
	(x, y) = coords

	for i, line in enumerate(lines):
		(w, h) = cv2.getTextSize(line, font, fontScale=fontScale, thickness=thickness)[0]
		y = coords[1] + h*i
		cv2.rectangle(img, (x-5, y-h), (x+w+5, y+5), bgColor, cv2.FILLED)

	h += 2
	for i, line in enumerate(lines):
		y = coords[1] + h*i
		cv2.putText(img, line, (x, y), font, fontScale, fontColor, thickness, cv2.LINE_AA)