"""
ORQUESTADOR P2P V1.1 — Malla Soberana Encriptada
Protocolo sobre WebSockets/TCP con cifrado AES-256-GCM nativo.
"""
import json
import time
import threading
import logging
import socket
from src.clawcore_system.neuronas.seguridad_soberana import seguridad

logger = logging.getLogger("OrquestadorP2P")
logger.setLevel(logging.INFO)


class PeerNode:
    """Representa un nodo remoto en la malla."""
    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.last_heartbeat = time.time()
        self.alive = True

    def is_stale(self, timeout=15):
        return (time.time() - self.last_heartbeat) > timeout


class OrquestadorP2P:
    """Gestiona la malla de nodos soberanos con cifrado obligatorio."""

    def __init__(self, my_id: str = "imac-primary", listen_port: int = 19000):
        self.my_id = my_id
        self.listen_port = listen_port
        self.peers: dict[str, PeerNode] = {}
        self._running = False
        self._server_thread = None
        self._hb_thread = None

    def registrar_peer(self, node_id: str, host: str, port: int):
        self.peers[node_id] = PeerNode(node_id, host, port)
        logger.info(f"🔗 Peer registrado: {node_id} @ {host}:{port}")

    def iniciar(self):
        self._running = True
        self._server_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._server_thread.start()
        self._hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._hb_thread.start()
        logger.info(f"🔱 Malla P2P SEGURA activa en puerto {self.listen_port}")

    def detener(self):
        self._running = False
        logger.info("🛑 Malla P2P detenida.")

    def _listen_loop(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", self.listen_port))
        srv.listen(5)
        srv.settimeout(1)
        while self._running:
            try:
                conn, addr = srv.accept()
                raw_data = conn.recv(8192).decode()
                # DESCIFRADO OBLIGATORIO
                decrypted_json = seguridad.desencriptar_payload(raw_data)
                if decrypted_json == "[ERROR_CIFRADO]":
                    logger.warning(f"🛡️ Intento de conexión no cifrada bloqueado desde {addr}")
                    conn.close()
                    continue
                
                msg = json.loads(decrypted_json)
                self._handle_message(msg, conn)
                conn.close()
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"P2P listen error: {e}")
        srv.close()

    def _handle_message(self, msg: dict, conn: socket.socket):
        mtype = msg.get("type")
        sender = msg.get("node_id", "unknown")

        if mtype == "HEARTBEAT":
            if sender in self.peers:
                self.peers[sender].last_heartbeat = time.time()
                self.peers[sender].alive = True
            resp_msg = json.dumps({"type": "HEARTBEAT_ACK", "node_id": self.my_id})
            conn.sendall(seguridad.encriptar_payload(resp_msg).encode())

        elif mtype == "STATUS":
            resp_msg = json.dumps({"type": "STATUS_RESP", "node_id": self.my_id,
                                "peers": len(self.peers),
                                "alive_peers": sum(1 for p in self.peers.values() if p.alive)})
            conn.sendall(seguridad.encriptar_payload(resp_msg).encode())

        elif mtype == "MIGRATE":
            logger.info(f"📦 Solicitud de migración cifrada desde {sender}")
            resp_msg = json.dumps({"type": "MIGRATE_ACK", "status": "received"})
            conn.sendall(seguridad.encriptar_payload(resp_msg).encode())

    def _heartbeat_loop(self):
        while self._running:
            for pid, peer in list(self.peers.items()):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((peer.host, peer.port))
                    # CIFRADO DE SALIDA
                    msg = json.dumps({"type": "HEARTBEAT", "node_id": self.my_id})
                    s.sendall(seguridad.encriptar_payload(msg).encode())
                    
                    raw_resp = s.recv(2048).decode()
                    resp = seguridad.desencriptar_payload(raw_resp)
                    if resp != "[ERROR_CIFRADO]":
                        peer.last_heartbeat = time.time()
                        peer.alive = True
                    s.close()
                except Exception:
                    if peer.is_stale():
                        peer.alive = False
                        logger.warning(f"💀 Peer {pid} fuera de línea.")
            time.sleep(5)

    def enviar_migracion(self, target_id: str, payload: dict) -> bool:
        peer = self.peers.get(target_id)
        if not peer or not peer.alive:
            return False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((peer.host, peer.port))
            msg = json.dumps({"type": "MIGRATE", "node_id": self.my_id, "payload": payload})
            s.sendall(seguridad.encriptar_payload(msg).encode())
            
            raw_resp = s.recv(4096).decode()
            resp_json = seguridad.desencriptar_payload(raw_resp)
            if resp_json == "[ERROR_CIFRADO]": return False
            
            resp = json.loads(resp_json)
            s.close()
            return resp.get("status") == "received"
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

    def reporte(self):
        return {
            "my_id": self.my_id,
            "port": self.listen_port,
            "peers_total": len(self.peers),
            "peers_alive": sum(1 for p in self.peers.values() if p.alive),
            "security": "AES-256-GCM Active"
        }


if __name__ == "__main__":
    mesh = OrquestadorP2P()
    mesh.registrar_peer("vps-1", "127.0.0.1", 19001)
    mesh.iniciar()
    print(json.dumps(mesh.reporte(), indent=2))
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        mesh.detener()
