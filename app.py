import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedTk
from tkcalendar import DateEntry
import tomograf as tm
import pydicom as dic
from datetime import datetime

from PIL import Image, ImageTk

class Application(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        
        self.configure(background="#f5f6f7")

        self.title("Tomograf")
        self.geometry("1000x850")

        self.file_path = None
        
        self.left_panel = ttk.Frame(self)
        self.left_panel.pack(side=tk.LEFT,expand=False,fill="y")

        self.file_frame = ttk.Frame(self.left_panel)
        self.file_frame.pack(pady=10)

        self.choose_button = ttk.Button(self.file_frame, text="Wybierz plik", command=self.choose_file)
        self.choose_button.pack(side=tk.TOP)

        self.file_label = ttk.Label(self.file_frame, text="")
        self.file_label.pack(side=tk.BOTTOM)

        self.entry_frame = ttk.Frame(self.left_panel)
        self.entry_frame.pack(pady=10)

        self.step_entry = self.create_entry(self.entry_frame, "Krok alfa")
        self.step_entry.insert(0, '1')
        self.emitter_range_entry = self.create_entry(self.entry_frame, "Rozpiętość układu emiter/detektor")
        self.emitter_range_entry.insert(0, '180')
        self.num_of_detectors_entry = self.create_entry(self.entry_frame, "Liczba dekoderów")
        self.num_of_detectors_entry.insert(0, '180')
        self.num_of_scans_entry = self.create_entry(self.entry_frame, "Liczba skanów")
        self.num_of_scans_entry.insert(0, '360')

        self.checkbox_frame = ttk.Frame(self.left_panel)
        self.checkbox_frame.pack(pady=10)

        self.filter_var = tk.IntVar()
        self.filter_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Użyj filtrowania", variable=self.filter_var)
        self.filter_checkbox.pack(side=tk.LEFT)
        self.animation_var = tk.IntVar()
        self.filter_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Animuj", variable=self.animation_var)
        self.filter_checkbox.pack(side=tk.LEFT)
        self.dicom_var = tk.IntVar()
        self.dicom_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Wygeneruj DICOM", command=self.toggle_dicom_fields, variable=self.dicom_var)
        self.dicom_checkbox.pack(side=tk.LEFT)

        self.dicom_fields_frame = ttk.Frame(self.left_panel)
        self.dicom_fields_frame.pack(pady=10)

        self.name_entry = self.create_entry(self.dicom_fields_frame, "Imię i nazwisko pacjenta")
        self.id_entry = self.create_entry(self.dicom_fields_frame, "ID pacjenta")
        
        
        date_frame = ttk.Frame(self.dicom_fields_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        date_label = ttk.Label(date_frame, text="Data badania")
        date_label.pack(side=tk.TOP)
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, selectbackground='red')
        self.date_entry.pack(side=tk.BOTTOM)

        self.comment_entry = self.create_entry(self.dicom_fields_frame, "Komentarz do badania")

        self.dicom_fields_frame.pack_forget()

        # koniec sekcji DICOM
        self.simulate_button = ttk.Button(self.left_panel, text="Uruchom", command=self.run_simulation, width=30)
        self.simulate_button.pack(pady=10)

        # sekcja zdjęć

        self.right_panel = ttk.Frame(self)
        self.right_panel.pack(side=tk.TOP,expand=False,fill="y")

        self.pb = ttk.Progressbar(self.right_panel,orient='horizontal',mode='determinate',length=300)
        self.pb.pack(side=tk.TOP,pady=10)
        self.pb_label = ttk.Label(self.right_panel, text="",font=(25) )
        self.pb_label.pack(side=tk.TOP,pady=(2,0))

        self.photo_frame_up = ttk.Frame(self.right_panel)
        self.photo_frame_up.pack(side=tk.TOP,pady=10)

        self.photo_frame2 = ttk.Frame(self.photo_frame_up,width=100, height=100)
        self.photo_frame2.pack(side=tk.LEFT,padx=10)
        self.photo_frame2_text = ttk.Label(self.photo_frame2, text="Wejściowy")
        self.photo_frame2_text.pack()

        self.photo_frame3 = ttk.Frame(self.photo_frame_up,width=100, height=100)
        self.photo_frame3.pack(side=tk.RIGHT,padx=10)
        self.photo_frame3_text = ttk.Label(self.photo_frame3, text="Sinogram")
        self.photo_frame3_text.pack()


        self.photo_frame_down = ttk.Frame(self.right_panel)
        self.photo_frame_down.pack(side=tk.TOP,pady=10)

        self.photo_frame4 = ttk.Frame(self.photo_frame_down,width=100, height=100)
        self.photo_frame4.pack(side=tk.LEFT,padx=10)
        self.photo_frame4_text = ttk.Label(self.photo_frame4, text="Przefiltrowany Sinogram")
        self.photo_frame4_text.pack()

        self.photo_frame5 = ttk.Frame(self.photo_frame_down,width=100, height=100)
        self.photo_frame5.pack(side=tk.RIGHT,padx=10)
        self.photo_frame5_text = ttk.Label(self.photo_frame5, text="Wyjściowy")
        self.photo_frame5_text.pack()

    def toggle_dicom_fields(self):
        if self.dicom_fields_frame.winfo_viewable():
            self.dicom_fields_frame.pack_forget()
        else:
            self.dicom_fields_frame.pack()

    def progress(self,val):
        if self.pb['value'] < 100:
            self.pb['value'] = val
        self.update()
    
    def set_label_progress(self,val):
        self.pb_label.config(text=val)
        self.update()

    def choose_file(self):
        self.name_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)
        self.im = None
        self.file_path = filedialog.askopenfilename(filetypes=[("Obraz", ".jpg .png"),("DICOM", ".dcm")])
        self.file_label.config(text=self.file_path)
        if self.file_path[-4:] == ".dcm":
            dcm = dic.dcmread(self.file_path)
            self.im = tm.normalize(dcm.pixel_array) # wydobycie danych pikseli z pliku dicom + normalizacja
            print(dcm)
            self.name_entry.insert(0, dcm.PatientName.family_comma_given())
            self.id_entry.insert(0, dcm.get('PatientID', 'BRAK')) 
            self.date_entry.set_date(datetime.strptime(dcm.get('StudyDate', ''), '%m/%d/%y').date())
            if (0x0010, 0x4000) in dcm:
                self.comment_entry.insert(0,dcm[0x00104000].value)

    def create_entry(self, parent, text):
        frame = ttk.Frame(parent)

        label = ttk.Label(frame, text=text)
        label.pack(side=tk.TOP,pady=(2,0))

        entry = ttk.Entry(frame)
        entry.pack(side=tk.TOP,pady=(2,0))

        #frame.pack(side=tk.LEFT, padx=20)
        frame.pack(padx=20)

        return entry
    
    def show_mse(self, mse):
        for widget in self.mse_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.mse_frame, text="RMSE: " + str(mse)).pack(side="top")
    
    def image_fit_to_show(self,im,flag=False):
        if flag:
            norm = tm.normalize(im)
            img = Image.fromarray(norm)
        else:
            img = Image.fromarray(im)
        img.thumbnail((300,300))
        return ImageTk.PhotoImage(img)

    def run_simulation(self):
        self.set_label_progress("")
        self.progress(0)
        if hasattr(self, "img1_label"):
            self.img1_label.pack_forget()
            self.img2_label.pack_forget()
            if hasattr(self, "img4_label"):
                self.img4_label.pack_forget()
            self.img5_label.pack_forget()
        if self.file_path==None:
            self.pb_label.config(text="NIE WYBRANO PLIKU")
            return
        animation = False
        if self.animation_var.get() == 1:
            animation = True
        if self.im is None:
            self.im = tm.loadImage(self.file_path) # ładowanie pliku + normalizacja
        img = self.image_fit_to_show(self.im)
        self.img1_label = ttk.Label(self.photo_frame2, image=img)
        self.img1_label.image = img
        self.img1_label.pack()
        self.update()

        self.img2_label = ttk.Label(self.photo_frame3, image=img)
        # utworzenie sinogramu
        sinogram = tm.radonTransform(self.im,t=self,img_label=2,animating=animation,numOfScans=int(self.num_of_scans_entry.get()),alphaShift=int(self.step_entry.get()),emitterRange = int(self.emitter_range_entry.get()), numOfDetectors = int(self.num_of_detectors_entry.get()) )
        self.showImage(sinogram,2)

        if self.filter_var.get() == 1: # filtrowanie sinogramu
            self.img4_label = ttk.Label(self.photo_frame4, image=img)
            tm.filtr(sinogram,t=self,animating=animation,img_label=4)
            self.showImage(sinogram,4,flag=True)

        self.img5_label = ttk.Label(self.photo_frame5, image=img)
        # rekonstrukcja obrazu z wykorzystaniem odwr. transf. Radona
        reconstructed = tm.inverseRadonTransform(sinogram,self.im,t=self,img_label=5,animating=animation,numOfScans=int(self.num_of_scans_entry.get()),alphaShift=int(self.step_entry.get()),emitterRange = int(self.emitter_range_entry.get()), numOfDetectors = int(self.num_of_detectors_entry.get()) )
        self.showImage(reconstructed,5)
        if self.dicom_var.get() == 1: # wywołanie zapisu do pliku
            tm.jpg_to_dcm(reconstructed,self.name_entry.get(),self.id_entry.get(),self.date_entry.get(),self.comment_entry.get())
        else:
            Image.fromarray(reconstructed).convert("L").save("output.png")

    def showImage(self,im,img_l,flag=False):
        match img_l:
            case 2:
                img_label = self.img2_label
            case 4:
                img_label = self.img4_label
            case 5:
                img_label = self.img5_label

        img2 = self.image_fit_to_show(im,flag=flag)
        img_label.configure(image=img2)
        img_label.image = img2
        img_label.pack()
        self.update()