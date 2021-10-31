#%%
#將Dicom轉換成Jpg
def emptydir(dirname):  #清空資料夾
    if os.path.isdir(dirname):  #資料夾存在就刪除
        shutil.rmtree(dirname)  #刪除資料夾
        sleep(2)  #需延遲,否則會出錯
    os.mkdir(dirname)  #建立資料夾

import pydicom as dicom
import os
import cv2
import PIL # 可選
import shutil, os
from time import sleep

# 轉換成JPG
# 指定.dcm文件夾路徑
folder_path = "Raw"
# 指定輸出jpg/png文件夾路徑
jpg_folder_path = "convert"
emptydir(jpg_folder_path)
images_folder_path = os.listdir(folder_path)
print("images_folder_path = ",images_folder_path)
# images_folder_path =  ['ESO-051(O)', 'ESO-052(O)', 'ESO-053(O)']

for i in images_folder_path:
    full_images_path =folder_path + "\\" + i
    print("full_images_path = ",full_images_path)
    # full_images_path =  D:/Raw/ESO-051(O)
    
    images_path = os.listdir(full_images_path)
    print("images_path = ",images_path)
    # images_path =  ['I430.dcm', 'I440.dcm', 'I300.dcm', 'I100.dcm'.....
    
    emptydir(jpg_folder_path +"\\" + i)
    
    for image in images_path:
        ds = dicom.dcmread(os.path.join(full_images_path, image)) # 讀取dicom
        pixel_array_numpy = ds.pixel_array
        image = image. replace('.dcm', '.jpg') #更改副檔名
        pixel_array_numpy = cv2.cvtColor(pixel_array_numpy, cv2.COLOR_RGB2BGR) #讀取檔案是RGB 轉成opencv的BGR
        cv2.imwrite(os.path.join(jpg_folder_path +"\\" + i, image), pixel_array_numpy) #存檔

#%%
#選取圖片中需要的部分 ROI
import cv2
import os
import glob  #找檔案
path = (glob.glob("convert/ESO-052(O)/*.jpg"))
path
# 'convert/ESO-052(O)\\I10.jpg',
#  'convert/ESO-052(O)\\I100.jpg',
#  'convert/ESO-052(O)\\I110.jpg',
#  'convert/ESO-052(O)\\I120.jpg',
pic = path[0]
pic
#'convert/ESO-052(O)\\I10.jpg'
# 讀取第一章照片
im = cv2.imread(pic)
# Select ROI
r = cv2.selectROI(im)
#計算矩形座標
(x, y, w, h) = r
#查看矩形座標是否正確
imCrop = im[y: y + h, x:x + w] # 裁切圖片
print(r)
cv2.imshow("Image", imCrop) #顯示圖片
cv2.waitKey(10000)
cv2.destroyAllWindows()
checked = int(input('繼續請輸入 1：'))
if checked == 1:
    output_folder = 'ROI/'+path[0][8:19]
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    # 資料夾中所有圖片自動裁切
    for i in path:
        image_read = cv2.imread(i)
        roiImg = image_read[y: y + h, x:x + w]
        cv2.imwrite(output_folder+i[19:], roiImg)
else:
    print("program shutdown")

#%%
#將亮點標記
#讀取圖片路徑
path = (glob.glob("ROI/ESO-052(O)/*.jpg")) #匯入所有jpg圖片路徑
print(path)
output_folder = 'bright spot/'+path[0][4:15] #建立一個輸出資料夾名稱
if not os.path.exists(output_folder): os.makedirs(output_folder) #如果目錄下沒有輸出資料夾，就創建一個
#迴圈一筆筆讀取
#i每跑一次就收到一張圖片路徑
for i in path:
    img = cv2.imread(i) #讀取i路徑
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #RGB轉灰階
    blur = cv2.GaussianBlur(gray, (41,41), 0) #高斯模糊除雜訊，(41,41)為模糊程度
    #開始找最大像素點(亮點座標)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur) #能夠回傳最小、大的像素值和座標
    minVal
    # 0.0
    maxVal
    # 163.0
    minLoc
    # (0, 0)
    maxLoc
    # (529, 342)
    #判斷是否為亮點 最大值175是不斷嘗試出來的
    if maxVal >= 175:
        cv2.circle(img, maxLoc, 41, (255, 0, 0), 2) #在座標上畫一個圓
        cv2.putText(img, str(i), (400,300), cv2.FONT_HERSHEY_SIMPLEX, 1,
		(50, 168, 82), 2, cv2.LINE_AA) #cv2.putText(影像, 文字, 座標, 字型, 大小, 顏色, 線條寬度, 線條種類)
        cv2.imwrite(output_folder + i[15:], img) #儲存亮點照片
        cv2.imshow("results", img) #秀出圖片
        cv2.waitKey(1000) #圖片顯示持續時間(單位毫秒)，0為一直顯示
        cv2.destroyAllWindows()
    else:
        #儲存沒有亮點的照片
        cv2.imwrite(output_folder + i[15:], img)

#%%
#二值化圖片以求得腫瘤亮點面積
path = (glob.glob("ROI/ESO-052(O)/*.jpg"))
output_folder = "thresh/"+path[0][4:15]
if not os.path.exists(output_folder): os.makedirs(output_folder)
for i in path:
    image = cv2.imread(i)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #將圖片轉成灰階
    blur = cv2.GaussianBlur(gray, (41,41),0) #高斯模糊
    # 腫瘤與背景分離的二值化處理
    thresh = cv2.threshold(blur, 175, 255, cv2.THRESH_BINARY)[1] #175是亮點亮度
    cv2.imwrite(output_folder + i[15:], thresh)

#%%
#使用Canny演算法計算腫瘤面積
path = (glob.glob("thresh/ESO-052(O)/*.jpg"))
f = open("area.txt", "w") #串建txt準備儲存面積數值
#f = open('檔案', '模式’)  模式”w”為新建檔案
for i in path:
    image = cv2.imread(i)
    edged = cv2.Canny(image, 175, 255) #Canny演算法，算出邊緣。175下限閥值
    #確認邊緣訊息
    (contours,_) = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #cv2.RETR_EXTERNAL外部輪廓；CHAIN_APPROX_SIMPLE簡單輪廓
    print(contours)
    # findContours 查找輪廓  
    # cv2.RETR_EXTERNAL 只找出外輪廓  
    # cv2.CHAIN_APPROX_SIMPLE 壓縮水平方向，垂直方向，對角線方向的元素，只保留該方向的終點座標
    if contours != []:
        area = cv2.contourArea(contours[0]) #計算面積area
        print("面積: %.2f" %area)
        value = "%s = %.2f" %(i, area) + "\n" #我要寫入txt的格式
        f.write(value) #寫入
f.close()

#%%
# 將contours的輪廓畫出來
# 計算不固定形狀面積
path = (glob.glob("thresh/ESO-052(O)/I480.jpg"))
for i in path:
    image = cv2.imread(i)
    edged = cv2.Canny(image, 175, 255) #Canny演算法，算出邊緣。175下限閥值
    #確認邊緣訊息
    (contours,_) = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # cv2.RETR_EXTERNAL外部輪廓；CHAIN_APPROX_SIMPLE簡單輪廓
    cv2.drawContours(image,contours,-1,(255,0,0),3,lineType=cv2.LINE_AA)
    # cv2.drawContours(圖片,輪廓,繪製哪條輪廓(-1為全畫),顏色,粗度,輪廓線型(cv2.LINE_AA 是反鋸齒線))
    cv2.imshow("Contours",image)
    cv2.waitKey()
    cv2.destroyAllWindows()
        














