import cv2
import imutils
from imutils.perspective import four_point_transform
import numpy as np

#读入图片
# image = cv2.imread("img2.jpg")

def getFourPtTrans(img):
    '''
    返回最大矩形框的极点坐标矩阵(4,2)
    '''
    #转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #高斯滤波
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    #自适应二值化方法
    blurred=cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,2)

    #canny边缘检测
    edged = cv2.Canny(blurred, 10, 100)

    # 从边缘图中寻找轮廓，然后初始化答题卡对应的轮廓
    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    docCnt = None

    # 确保至少有一个轮廓被找到
    if len(cnts) > 0:
        # 将轮廓按大小降序排序
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        # 对排序后的轮廓循环处理
        for c in cnts:
            # 获取近似的轮廓
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # 如果近似轮廓有四个顶点，那么就认为找到了答题卡
            if len(approx) == 4:
                docCnt = approx
                break


    docCnt=docCnt.reshape(4,2)
    return docCnt

def getXY(docCnt):
    '''return (minX,minY,maxX,maxY)'''
    minX,minY=docCnt[0]
    maxX,maxY=docCnt[0]
    for i in range(1,4):
        minX=min(minX,docCnt[i][0])
        maxX=max(maxX,docCnt[i][0])
        minY=min(minY,docCnt[i][1])
        maxY=max(maxY,docCnt[i][1])
    return minX,minY,maxX,maxY

# 判断题号
def judgeQ(x,y):
    '''传入时记得x+1,y+1'''
    if x<6:
        return x+(y-1)//4*5
    else:
        return ((x-1)//5-1)*25+10+(x-1)%5+1+(y-1)//4*5

# 判断答案
def judgeAns(y):
    if y%4==1:
        return 'A'
    if y%4==2:
        return 'B'
    if y%4==3:
        return 'C'
    if y%4==0:
        return 'D'

def judge0(x,y):
    return (judgeQ(x,y),judgeAns(y))


# 人工标记答题卡格子的边界坐标
xt1=[0,110,210,310,410,565,713,813,913,1013,1163,1305,1405,1505,1605,1750,1895,1995,2095,2195,2295]
yt1=[0,125,175,225,300,422,471,520,600,716,766,817,902,1012,1064,1113,1195,1309,1357,1409,1479]

def markOnImg(img,width,height):
    '''在四点标记的图片上，将涂黑的选项标记，并返回(图片,坐标)'''
    docCnt=getFourPtTrans(img)
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    paper=four_point_transform(img,docCnt)
    warped=four_point_transform(gray,docCnt)

    # 灰度图二值化
    thresh=cv2.adaptiveThreshold(warped,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,2)
    # resize
    thresh = cv2.resize(thresh, (width, height), cv2.INTER_LANCZOS4)
    paper = cv2.resize(paper, (width, height), cv2.INTER_LANCZOS4)
    warped = cv2.resize(warped, (width, height), cv2.INTER_LANCZOS4)

    ChQImg = cv2.blur(thresh, (13, 13))
    # 二值化，120是阈值
    ChQImg = cv2.threshold(ChQImg, 120, 225, cv2.THRESH_BINARY)[1]
    # cv2.imwrite("paper.jpg",paper)
    Answer=[]

    # 二值图中找答案轮廓
    cnts=cv2.findContours(ChQImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnts=cnts[1] if imutils.is_cv3() else cnts[0]
    for c in cnts:
        x,y,w,h=cv2.boundingRect(c)
        if w>50 and h>20 and w<100 and h<100:
            M=cv2.moments(c)
            cX=int(M["m10"]/M["m00"])
            cY=int(M["m01"]/M["m00"])

            cv2.drawContours(paper,c,-1,(0,0,255),5)
            cv2.circle(paper,(cX,cY),7,(255,255,255),2)
            Answer.append((cX,cY))
    return paper,Answer


def solve(imgPath):
    '''传入图片，返回(image(准考证号,科目,答题),(考号,科目名,[答案选择情况]))'''

    # 这里能识别到的最大方框是答题部分的方框，然后根据这个方框就可以推断出其他方框的大致位置。
    image=cv2.imread(imgPath)
    # 搞到答案的四点坐标
    ansCnt=getFourPtTrans(image)
    xy=getXY(ansCnt)
    # ansImg=image[xy[1]:xy[3],xy[0]:xy[2]]
    # ansImg=four_point_transform(image,ansCnt)
    # ansImg=cv2.resize(ansImg,(800,600))
    # cv2.imshow("ans",ansImg)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    xy=getXY(ansCnt)
    # 切取上半部分的图
    stuNum=image[0:xy[1],xy[0]:xy[2]]
    numCnt=getFourPtTrans(stuNum)
    # cv2.imshow("stuNum",cv2.resize(stuNum.copy(),(600,800)))
    # cv2.imshow("stu_f",cv2.resize(four_point_transform(stuNum,numCnt),(600,800)))

    xy=getXY(numCnt)
    # 切右半部分的图，方便识别科目
    course=image[0:int(xy[3]*1.1),xy[2]:len(image)]
    # 搞到科目矩形的四点
    # courseCnt=getFourPtTrans(course)
    # cv2.imshow("course",cv2.resize(course.copy(),(600,800)))
    # cv2.imshow("course_f",cv2.resize(four_point_transform(course,courseCnt),(600,800)))


    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # print(image.size)
    # cv2.drawContours(image,docCnt,-1,(0,0,255),50)

    '''处理答案'''
    width1,height1=2300,1500
    ansImg,Answer=markOnImg(image,width1,height1)

    # [(题号，答题卡上的答案),]
    IDAnswer=[]
    for a in Answer:
        for x in range(0,len(xt1)-1):
            if a[0]>xt1[x] and a[0]<xt1[x+1]:
                for y in range(0,len(yt1)-1):
                    if a[1]>yt1[y] and a[1]<yt1[y+1]:
                        IDAnswer.append(judge0(x+1,y+1))

    IDAnswer.sort()
    ansImg=cv2.resize(ansImg,(600,400))
    # cv2.imshow("answer",ansImg)
    # cv2.imwrite("answer.jpg",ansImg)
    # print(IDAnswer)


    '''处理学号'''
    width2,height2=1000,1000
    numImg,Answer=markOnImg(stuNum,width2,height2)

    Answer.sort()
    # xt2=list(range(0,1100,100))
    yt2=[227,311,374,442,509,577,644,711,781,844]

    NO=''
    for a in Answer:
        for y in range(len(yt2)-1):
            if a[1]>yt2[y] and a[1]<yt2[y+1]:
                NO+=str(y)
    if NO=='':
        NO="Nan"
    numImg=cv2.resize(numImg,(300,200))
    # cv2.imshow('SNO',numImg)
    # print(NO)

    '''处理科目'''
    width3,height3=300,1000
    courseImg,Answer=markOnImg(course,width3,height3)
    yt3=list(range(250,1000,65))
    course_list=['政治','语文','数学','物理','化学','英语',
        '历史','地理','生物','文综','理综']

    s=-1
    if len(Answer)>0:
        for y in range(len(yt3)-1):
            if Answer[0][1]>yt3[y] and Answer[0][1]<yt3[y+1]:
                s=y

    courseImg=cv2.resize(courseImg,(150,400))
    # cv2.imshow('course',courseImg)
    course_checked="Nan"
    if s!=-1:
        course_checked=course_list[s]


    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return ((numImg,courseImg,ansImg),(NO,course_checked,IDAnswer))

if __name__ == "__main__":
    (numImg,courseImg,ansImg),(NO,course,IDAnswer)=solve("img2.jpg")
    cv2.imshow("answer",ansImg)
    cv2.imshow('SNO',numImg)
    cv2.imshow('course',courseImg)
    print(NO)
    print(course)
    print(IDAnswer)
    cv2.waitKey()
    cv2.destroyAllWindows()
    cv2.destroyAllWindows()
    