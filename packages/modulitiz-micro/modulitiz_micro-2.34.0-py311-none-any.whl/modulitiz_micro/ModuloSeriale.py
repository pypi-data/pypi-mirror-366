import serial

from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class ModuloSeriale(object):
	"""
	Utility di gestione dela connessione seriale RS232
	"""
	
	COM_PORTS=[]
	
	def __init__(self):
		self.connessione=None
	
	@classmethod
	def populate(cls):
		"""
		Popola le variabili di classe.
		"""
		if ModuloSystem.isWindows():
			COM_PORTS=cls.__generaElencoPorte("COM",1)
		else:
			COM_PORTS=cls.__generaElencoPorte("/dev/tty",0)
			COM_PORTS.extend(cls.__generaElencoPorte("/dev/ttyS",0))
			COM_PORTS.extend(cls.__generaElencoPorte("/dev/ttyUSB",0))
		cls.COM_PORTS=COM_PORTS
	
	def apriPrimaPortaDisponibile(self):
		"""
		Prova ad aprire la prima porta disponibile che trova.
		"""
		for porta in self.COM_PORTS:
			try:
				connessioneSeriale=serial.Serial(port=porta, baudrate=9600, rtscts=True, dsrdtr=True, exclusive=True)
				connessioneSeriale.dtr=True
				connessioneSeriale.dtr=False
				self.connessione=connessioneSeriale
				return
			except (OSError,serial.SerialException):
				pass
	
	def isOpen(self)->bool:
		"""
		Controlla se la connessione alla porta è aperta.
		"""
		return self.connessione is not None and self.connessione.isOpen()
	
	def close(self):
		"""
		Chiude la connessione alla porta.
		"""
		if not self.isOpen():
			return
		self.connessione.close()
		self.connessione=None

	@staticmethod
	def __generaElencoPorte(prefisso:str,inizio:int)->list:
		return [prefisso+str(i) for i in range(inizio,16)]
	
