import math
import skimage as sk
import matplotlib.pyplot as plt
import numpy as np
import pydicom as dic
import copy
import datetime


def normalize(im): # normalizacja
  norm = np.zeros(shape=(im.shape))
  im_max = im.max()
  im_min = 0
  for x in range(im.shape[0]):
    norm[x] = np.interp(im[x], (im_min, im_max), (0, 255))
  return norm

def loadImage(imgPath): # ładuje obrazek
  im = sk.io.imread(imgPath, as_gray=True)
  im = normalize(im)
  return im

def showImage(im,animating=False): # drukuje obrazek, normalizując zakres wartości
  if animating==True:
      im = normalize(copy.deepcopy(im))
  vmax = im.max()
  plt.imshow(im, cmap='gray', vmin=0.0, vmax=vmax);  # Średnik na końcu zmienia output??? WTF??!!
  plt.show()

def showImage2(im,animating=False,i=1): # drukuje obrazek, normalizując zakres wartości
  if animating==True:
      im = normalize(copy.deepcopy(im))
  vmax = im.max()
  plt.figure(i)
  return plt.imshow(im, cmap='gray', vmin=0.0, vmax=vmax).figure;  # Średnik na końcu zmienia output??? WTF??!!

def bresenham(img,x1,y1,x2,y2): # algorytm Bresenhama, zwraca średnią jasność
  max_x = len(img)
  max_y = len(img[0])
  sum = 0
  n = 0
  x = x1
  x_inc = 1 # inkrement
  dx = x2 - x1 # przesunięcie
  y = y1
  y_inc = 1
  dy = y2 - y1
  if x1>=x2: # rysujemy w lewo, zamiast w prawo
    x_inc = -1
    dx = x1 - x2
  if y1>=y2: # rysujemy w dół, zamiast w górę
    y_inc = -1
    dy = y1 - y2
  if dx > dy: # oś wiodąca OX
    ep_inc_a = 2*(dy-dx)
    ep_inc_b = 2*dy
    ep = ep_inc_b - dx # błąd (odchylenie od współrzędnych całkowitych)
    while x!=x2:
      if not(x>=max_x or y>=max_y or x<0 or y<0): # sprawdzamy czy nie jesteśmy poza obrazkiem
        sum += img[x-1][y-1]
        n += 1
      if ep>=0:
        y += y_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      x += x_inc
  else: # oś wiodąca OY
    ep_inc_a = 2*(dx-dy)
    ep_inc_b = 2*dx
    ep = ep_inc_b - dy # błąd (odchylenie od współrzędnych całkowitych)
    x = x1
    while y!=y2:
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        sum += img[x-1][y-1]
        n += 1
      if ep>=0:
        x += x_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      y += y_inc
  try:
    a = sum/n
  except: # ¯\_(ツ)_/¯
    a = 0
  return a

def radonTransform(img,t,img_label, emitterRange = 180, numOfDetectors = 180, numOfScans = 180, alphaShift = 2, animating = False, animationInterval = 20):
  t.set_label_progress("Transformata Radona")
  alphaShift = math.radians(alphaShift)
  center = (len(img)//2, len(img[0])//2)
  #R = min(center)
  R = max(center) * math.sqrt(2)
  alpha = (2*math.pi*90)/360 # alpha emitera, zaczynamy od 90 stopni myślę i tu wystarczy potem dodawać to przesunięcie
  phi = (2*math.pi*emitterRange)/360 # kąt rozwarcia dla detektorów
  #print("E ({},{})".format(xe,ye))
  sinogram = np.zeros(shape=(numOfScans,numOfDetectors))
  for scan in range(numOfScans): # dla każdego skanu
    t.progress((scan/numOfScans)*100)
    # tutaj dla wzyznaczanych współrzędnych za każdym razem odnoszę się do środka, aby nie robić potem przesunięć tylko od razu
    xe = center[0] + round(R * math.cos(alpha))
    ye = center[1] - round(R * math.sin(alpha))
    for det in range(numOfDetectors): # dla każdego detektora
      xd = center[0] + round(R * math.cos(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      yd = center[1] - round(R * math.sin(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      #print("D{} ({},{})".format(i,xd,yd))
      sinogram[scan][det] = bresenham(img,xe,ye,xd,yd)
    alpha += alphaShift # wykonujemy przesunięcie
    if animating and scan % animationInterval == 0:
      t.showImage(normalize(sinogram),img_label)
      #showImage(sinogram,animating)
      
      
      #plotImage(sinogram,ax,animating=animation)
  return normalize(sinogram)

def inverseBresenham(max_x,max_y,x1,y1,x2,y2): # zwraca koordynaty pikseli między emiterem a detektorem
  coords = []
  x = x1
  x_inc = 1 # inkrement
  dx = x2 - x1 # przesunięcie
  y = y1
  y_inc = 1
  dy = y2 - y1
  if x1>=x2: # rysujemy w lewo, zamiast w prawo
    x_inc = -1
    dx = x1 - x2
  if y1>=y2: # rysujemy w dół, zamiast w górę
    y_inc = -1
    dy = y1 - y2
  if dx > dy: # oś wiodąca OX
    ep_inc_a = 2*(dy-dx)
    ep_inc_b = 2*dy
    ep = ep_inc_b - dx # błąd (odchylenie od współrzędnych całkowitych)
    while x!=x2:
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        coords.append((x-1,y-1))
      #print(f"({x} {y})")
      if ep>=0:
        y += y_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      x += x_inc
  else: # oś wiodąca OY
    ep_inc_a = 2*(dx-dy)
    ep_inc_b = 2*dx
    ep = ep_inc_b - dy # błąd (odchylenie od współrzędnych całkowitych)
    x = x1
    while y!=y2:
      #print(f"({x} {y})")
      if not(x>=max_x or y>=max_y or x<0 or y<0):
        coords.append((x-1,y-1))
      if ep>=0:
        x += x_inc
        ep += ep_inc_a
      else:
        ep += ep_inc_b
      y += y_inc
  return coords

def inverseRadonTransform(sinogram, img,t,img_label, emitterRange = 180, numOfDetectors = 180, numOfScans = 180, alphaShift = 2, animating = False, animationInterval=20):
  t.set_label_progress("Odwrotna Transformata Radona")
  alphaShift = math.radians(alphaShift)
  center = (img.shape[0]//2, img.shape[1]//2)
  #R = min(center)
  R = max(center) * math.sqrt(2)
  alpha = (2*math.pi*90)/360 # alpha emitera, zaczynamy od 90 stopni myślę i tu wystarczy potem dodawać to przesunięcie
  phi = (2*math.pi*emitterRange)/360 # kąt rozwarcia dla detektorów
  #print("E ({},{})".format(xe,ye))
  reconstructed = np.zeros(shape=img.shape)
  for scan in range(numOfScans): # dla każdego skanu (wzmocnienia)
    t.progress((scan/numOfScans)*100)
    # tutaj dla wzyznaczanych współrzędnych za każdym razem odnoszę się do środka, aby nie robić potem przesunięć tylko od razu
    xe = center[0] + round(R * math.cos(alpha))
    ye = center[1] - round(R * math.sin(alpha))
    for det in range(numOfDetectors): # dla każdego detektora
      xd = center[0] + round(R * math.cos(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      yd = center[1] - round(R * math.sin(alpha+math.pi-phi/2 + det*phi/(numOfDetectors-1)))
      #print("D{} ({},{})".format(i,xd,yd))
      coords = inverseBresenham(img.shape[0], img.shape[1],xe,ye,xd,yd)
      reconstructed[tuple(np.transpose(coords))] += sinogram[scan][det] # Numpy robi brrrrrrrrr
    alpha += alphaShift # wykonujemy przesunięcie
    if animating and scan % animationInterval == 0:
      t.showImage(normalize(reconstructed),img_label)
      #plotImage(sinogram,ax,animating=animation)
      mse, rmse = calcRMSE(img,normalize(reconstructed))
      t.set_label_progress(f"Odwrotna Transformata Radona\nRMSE: {rmse:.4f}")
      print(f"\nBłąd średniokwadratowy wynosi {mse:.2f}")
      print(f"RMSE wynosi {rmse:.2f}")
  mse, rmse = calcRMSE(img,normalize(reconstructed))
  t.set_label_progress(f"Odwrotna Transformata Radona\nRMSE: {rmse:.4f}")
  return normalize(reconstructed)

def filtr(sinogram,t,img_label, animating = False):
  t.set_label_progress("Filtrowanie")
  result = []
  for i in range(1,11):
    if i%2==0:
      result.append(0)
    else:
      result.append(-4/pow(math.pi,2)/pow(i,2))
  res2 = result.copy()
  result.reverse()
  kernel = result + [1] + res2
  for i in range(sinogram.shape[0]):
    t.progress((i/sinogram.shape[0])*100)
    sinogram[i, :] = np.convolve(sinogram[i, :], kernel, mode="same")
    if animating:
      t.showImage(normalize(sinogram),img_label,flag=True)

def calcRMSE(im1, im2):
  mse = np.square(np.subtract(im1, im2)).mean()
  return (mse, math.sqrt(mse)) # (mse, rmse)

def jpg_to_dcm(reconstructed,name="BRAK",patient_id="0",date="",comment="BRAK"):
  # Meta tagi
  file_meta = dic.dataset.FileMetaDataset()
  file_meta.MediaStorageSOPClassUID = dic.uid.UID('1.2.840.10008.5.1.4.1.1.2')
  file_meta.MediaStorageSOPInstanceUID = dic.uid.generate_uid()
  file_meta.ImplementationClassUID = dic.uid.UID("1.2.826.0.1.3680043.8.498.1")

  dcm = dic.dataset.FileDataset("output.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)

  dcm.file_meta.TransferSyntaxUID = dic.uid.ImplicitVRLittleEndian
  dcm.is_little_endian = True
  dcm.is_implicit_VR = True

  # Zapisujemy!
  dt = datetime.datetime.now()
  if date == "":
    dcm.StudyDate = dt.strftime('%Y%m%d')
    dcm.ContentDate = dt.strftime('%Y%m%d')
  else:
    dcm.StudyDate = date
    dcm.ContentDate = date
  dcm.StudyTime = dt.strftime('%H%M%S')
  timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
  dcm.ContentTime = timeStr
  dcm.PatientName = name
  dcm.PatientID = patient_id
  dcm.StudyID = "1234"
  dcm.SeriesNumber = "1"

  dcm.PatientComments = comment

  dcm.SOPInstanceUID = dic.uid.generate_uid()
  dcm.SeriesInstanceUID = dic.uid.generate_uid()
  dcm.StudyInstanceUID = dic.uid.generate_uid()
  dcm.FrameOfReferenceUID = dic.uid.generate_uid()

  dcm.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
  dcm.Modality = "CT"
  dcm.Rows = reconstructed.shape[0]
  dcm.Columns = reconstructed.shape[1]
  dcm.BitsAllocated = 8
  dcm.BitsStored = 8
  dcm.HighBit = dcm.BitsStored - 1

  dcm.SamplesPerPixel = 1
  dcm.PhotometricInterpretation = 'MONOCHROME2'
  dcm.PixelRepresentation = 0

  dcm.PixelData = reconstructed.astype(np.uint8).tobytes()

  # Prywatne bloki do zapisania własnych danych
  block = dcm.private_block(0x000b, "PUT 151785 151741", create=True)
  block.add_new(0x01, "SH", comment)

  print(f"Nazwisko i imię pacjenta: {dcm.PatientName.family_comma_given()}")
  print(f"ID pacjenta: {dcm.get('PatientID', 'BRAK')}")
  print(f"Data badania: {dcm.get('StudyDate', 'BRAK')}")
  print(f"Rozmiar obrazu: {dcm.get('Rows', 'BRAK')} x {dcm.get('Columns', 'BRAK')}")
  if (0x000b, 0x0010) in dcm:
    print(f"Autorzy: {dcm[0x000b0010].value}")
  if (0x0010, 0x4000) in dcm:
    print(f"Komentarze: {dcm[0x00104000].value}")
  dcm.save_as("output.dcm", write_like_original=False)

def read_dcm(file):
  dcm = dic.dcmread(file)
  print(f"Nazwisko i imię pacjenta: {dcm.PatientName.family_comma_given()}")
  print(f"ID pacjenta: {dcm.get('PatientID', 'BRAK')}")
  print(f"Data badania: {dcm.get('StudyDate', 'BRAK')}")
  print(f"Rozmiar obrazu: {dcm.get('Rows', 'BRAK')} x {dcm.get('Columns', 'BRAK')}")
  if (0x000b, 0x0010) in dcm:
    print(f"Autorzy: {dcm[0x000b0010].value}")
  if (0x000b, 0x1001) in dcm:
    print(f"Komentarze: {dcm[0x000b1001].value}")
  print()
  showImage(dcm.pixel_array)