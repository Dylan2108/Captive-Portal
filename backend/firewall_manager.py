import subprocess

class FirewallManager:
    "Para gestionar las reglas del firewall usando iptables"
    def __init__(self,interface):
        self.interface = interface
        self.chain_name = "CAPTIVE PORTAL"
    
    def run_command(self,command):
        "Ejecuta un comando del sistema"
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
                timeout=10
            )
            return result.returncode == 0,result.stdout,result.stderr
        except subprocess.TimeoutExpired:
            return False,"","Timeout ejecutando comando"
        except Exception as e:
            return False,"",str(e)
    
    def setup_firewall(self):
        "Configura las reglas iniciales del firewall"
        print("Configurando firewall")

        commands = [
            "iptables -F",
            "iptables -t nat -F",
            "iptables -X",
            f"iptables -N {self.chain_name} 2>/dev/null || true",
            "iptables -A INPUT -i lo -j ACCEPT",
            "iptables -A OUTPUT -o lo -j ACCEPT",
            "iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
            "iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
            f"iptables -A INPUT -p tcp --dport {self.get_portal_port()} -j ACCEPT",
            "iptables -A INPUT -p udp --dport 53 -j ACCEPT",
            "iptables -A INPUT -p tcp --dport 53 -j ACCEPT",
            "iptables -A OUTPUT -p udp --dport 53 -j ACCEPT",
            "iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT",
            "iptables -A INPUT -p udp --dport 67:68 -j ACCEPT",
            "iptables -A OUTPUT -p udp --dport 67:68 -j ACCEPT",
            "iptables -P FORWARD DROP",
            f"iptables -t nat -A POSTROUTING -o {self.interface} -j MASQUERADE",
            "sysctl -w net.ipv4.ip_forward=1",
            "echo 1 > /proc/sys/net/ipv4/ip_forward"
        ]

        for command in commands:
            success , stdout , stderr = self.run_command(command)
            if not success and "exist" not in stderr.lower():
                print(f"Advertencia: {command}")
        
        print("Firewall configurado correctamente")

        return True
    
    def get_portal_port(self):
        "Obtiene el puerto del portal desde la configuracion"
        return 8080
    
    def allow_ip(self,ip_address):
        "Permite el trafico de una ip"
        check_cmd = f"iptables -I FORWARD -s {ip_address} -j ACCEPT 2>/dev/null"
        exists,_,_ = self.run_command(check_cmd)

        if exists:
            print(f"IP {ip_address} ya está autorizada")
            return True
        
        cmd = f"iptables -I FORWARD -s {ip_address} -j ACCEPT"
        success,_,stderr = self.run_command(cmd)

        if success:
            print(f"IP autorizada : {ip_address}")
        else:
            print(f"Error autorizando IP {ip_address}: {stderr}")

        return success

    def block_ip(self,ip_address):
        "Bloquea el trafico de una IP"
        cmd = f"iptables -D FORWARD -s {ip_address} -j ACCEPT 2>/dev/null"
        success,_,_ =  self.run_command(cmd)

        if success:
            print(f"IP Bloqueada : {ip_address}")
        else:
            print(f"IP {ip_address} no estaba autorizada")
        
        return True
    
    def is_ip_allowed(self,ip_address):
        "Verifica si una IP esta autorizada"
        cmd = f"iptables -C FORWARD -s {ip_address} -j ACCEPT 2>/dev/null"
        success,_,_ = self.run_command(cmd)
        return success
    
    def list_allowed_ips(self):
        "Lista las IP permitidas actualmente"
        success,output,_ = self.run_command("iptables -L FORWARD -n")

        if not success:
            return []
        
        ips = []
        for line in output.split('\n'):
            if 'ACCEPT' in line and '0.0.0.0/0' not in line:
                parts = line.split()
                if len(parts) >= 4:
                    source = parts[3]
                    if source != '0.0.0.0/0':
                        ips.append(source)
        
        return ips