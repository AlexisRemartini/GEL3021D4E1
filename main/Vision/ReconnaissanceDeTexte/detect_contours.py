import cv2


image = cv2.imread('/D4/media/images/general/jeuSwitchSurtable.jpg')
# image = cv2.imread('image-300x169.jpg')
###################################################################################
#conversion en niveaux de gris
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,250,255,cv2.THRESH_BINARY_INV)

contours,h = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

#key: figX, val = [contours, pointminHAUTGAUCHE, pointmaxBASDROITE)]
subfigures = {}
key = "fig"
n = 0
xs = []
ys = []
point0 = 0
point3 = 0
points_plus_clairs = []
fig_width = 0
fig_heigth = 0
for i in contours:
    if len(i)>2:
        for j in i:
            xs.append(j[0][0])
            ys.append(j[0][1])
            points_plus_clairs.append((j[0][0], j[0][1]))
            point0 = (min(xs), min(ys))
            point3 = (max(xs), max(ys))
            fig_width = abs(max(xs)-min(xs))
            fig_heigth = abs(max(ys)-min(ys))
        xs = []
        ys = []
        subfigures[key+str(n)] = [i, point0, point3, fig_width, fig_heigth]
        n = n + 1
print(subfigures)

cv2.drawContours(image, [subfigures["fig0"][0]], -1, (0,255,0), 2)
###################################################################################

# cX =0
# cY =0
#
# for cnt in contours:
#     perimetre = cv2.arcLength(cnt, True)
#     approx = cv2.approxPolyDP(cnt, 0.01 * perimetre, True)
#     try:
#         M = cv2.moments(cnt)
#         cX = int(M["m10"] / M["m00"])
#         cY = int(M["m01"] / M["m00"])
#         cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)
#     except(ZeroDivisionError):
#         pass
#     if len(approx) == 3:
#         shape = "triangle"
#     elif len(approx) == 4:
#         (x, y, w, h) = cv2.boundingRect(approx)
#         ratio = w / float(h)
#         if ratio >= 0.95 and ratio <= 1.05:
#             shape = "carre"
#         else:
#             shape = "rectangle"
#     elif len(approx) == 5:
#         shape = "pentagone"
#     elif len(approx) == 6:
#         shape = "hexagone"
#     else:
#         shape = "circle"
#     cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

# cont =contours[0]
# for i in cont:
#cv2.drawContours(image, contours[0:8], -1, (0, 255, 0), 2)

cv2.imshow("test", image)
cv2.waitKey(0)