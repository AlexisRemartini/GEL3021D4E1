import cv2
import pytesseract


img_add = 'D4\\main\\static\\main\\img\\produit01.jpg'
def process(img_adress):
    #https://www.murtazahassan.com/courses/opencv-projects/
    #control + left click
    pytesseract.pytesseract.tesseract_cmd = "/usr/local/Cellar/tesseract/4.1.1/bin/tesseract"

    img = cv2.imread(img_adress)
    #pytesseract only accept rgb, so we convert bgr to rgb
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    ##Detecting characters and their position
    #print(pytesseract.image_to_string(img))
    ##character xpoint ypoint width heigth
    #print(pytesseract.image_to_boxes(img))

    #taille
    hImg, wImg,_ = img.shape
    ##character xpoint ypoint width heigth
    boxes = pytesseract.image_to_boxes(img)
    boxes_splitted = boxes.splitlines()
    for b in boxes_splitted:
        #print(b)
        b = b.split(' ')
        x,y,w,h = int( b[1]), int(b[2]), int(b[3]),int(b[4])

        # cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 1)
        cv2.rectangle(img, (x,hImg - y), (w, hImg - h), (50, 50, 255), 2)

        #ecrire le caracteres dessus
        cv2.putText(img, b[0], (x, hImg - y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 255, 50), 2)

    # cv2.imshow('reult', img)
    # cv2.waitKey(0)

    boxes_splitted = pytesseract.image_to_string(img).splitlines()

    return (img, boxes_splitted)

#process(img_add)