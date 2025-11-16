import json
import hashlib
import os

class UserManager:
    #Gestiona usuarios del portal cautivo

    def __init__(self,dbfile):
        self.dbfile = dbfile
        self.ensure_directory()
        self.users = {}
        self.load_users()
    
    def ensure_directory(self):
        #Se asegura que existe el directorio de datos
        directory = os.path.dirname(self.dbfile)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def load_users(self):
        #Carga los usuarios desde el directorio de datos
        if os.path.exists(self.dbfile):
            try:
                with open(self.dbfile,'r') as f:
                    self.users = json.load(f)
                print(f"Usuarios cargados: {len(self.users)}")
            except Exception as e:
                print(f"Error cargando usuarios: {e}")
    
    def save_users(self):
        #Guarda los usuarios en el directorio de datos
        try:
            with open(self.dbfile,'w') as f:
                json.dump(self.users,f,indent=2)
        except Exception as e:
            print(f"Error guardando usuarios: {e}")
    
    def hash_password(self,password):
        #Genera hash SHA256 de la contraseña
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self,username,password):
        #Autentica un usuario
        if username in self.users:
            user_data = self.users[username]
            if user_data['password'] == self.hash_password(password):
                return{
                    'username' : username,
                    'email' : user_data.get('email','')
                }
        return None
    
    def add_user(self,username,password,email):
        #Añade un nuevo usuario
        if username in self.users:
            return False
        
        self.users[username] = {
            'password' : self.hash_password(password),
            'email' : email
        }
        self.save_users()
        print(f"Usuario añadido : {username}")
        return True
    
    def remove_user(self,username):
        #Elimina un usuario
        if username in self.users:
            del self.users[username]
            self.save_users()
            print(f"Usuario eliminado : {username}")
            return True
        return False
    
    def list_users(self):
        #Lista todos los usuarios
        return [
            {
                'username' : username,
                'email' : data.get('email','')
            } for username , data in self.users.items()
        ]
    
    def get_user_count(self):
        #Retorna el numero total de usuarios
        return len(self.users)