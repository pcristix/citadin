from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

class QRScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # Buton pentru a porni camera
        self.scan_button = Button(text='Deschide Camera și Scanează QR', size_hint=(1, 0.2))
        self.scan_button.bind(on_press=self.toggle_camera)
        
        # Etichetă pentru afișarea rezultatelor
        self.result_label = Label(text='Date scanate vor apărea aici', size_hint=(1, 0.2))
        
        # Camera (inițial invizibilă)
        self.camera = Camera(resolution=(640, 480), size_hint=(1, 0.6))
        self.camera.play = False
        self.camera.opacity = 0
        
        self.layout.add_widget(self.scan_button)
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.result_label)
        
        self.scanning = False
        return self.layout
    
    def toggle_camera(self, instance):
        if self.scanning:
            # Oprește scanarea
            self.scanning = False
            self.camera.play = False
            self.camera.opacity = 0
            self.scan_button.text = 'Deschide Camera și Scanează QR'
            Clock.unschedule(self.scan_frame)
        else:
            # Pornește scanarea
            self.scanning = True
            self.camera.play = True
            self.camera.opacity = 1
            self.scan_button.text = 'Oprește Scanarea'
            self.result_label.text = 'Scanare în curs...'
            Clock.schedule_interval(self.scan_frame, 1.0/30.0)  # 30 fps
    
    def scan_frame(self, dt):
        # Captură frame-ul din camera Kivy
        texture = self.camera.texture
        if texture:
            # Convertim textura Kivy într-o imagine OpenCV
            size = texture.size
            pixels = texture.pixels
            image = np.frombuffer(pixels, np.uint8)
            image = image.reshape((size[1], size[0], 4))  # RGBA format
            
            # Convertim din RGBA în BGR (pentru OpenCV)
            frame = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            # Detectăm codurile QR
            decoded_objects = pyzbar.decode(frame)
            
            for obj in decoded_objects:
                # Afișăm datele scanate
                data = obj.data.decode('utf-8')
                self.result_label.text = f'Date scanate: {data}'
                
                # Oprim scanarea după ce am găsit un cod QR
                self.toggle_camera(None)
                
                # Desenăm un dreptunghi în jurul codului QR (opțional)
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else:
                    hull = points
                
                n = len(hull)
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j+1) % n], (0, 255, 0), 3)
            
            # (Opțional) Afișăm frame-ul procesat (pentru debug)
            # cv2.imshow("QR Scanner", frame)
            # cv2.waitKey(1)

if __name__ == '__main__':
    QRScannerApp().run()