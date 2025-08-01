from requests.auth import HTTPBasicAuth
from epic.kicad import scripts

def main():
    auth = HTTPBasicAuth('admin', 'admin')
    scripts.epic_bom('http://localhost:8000/epic/api/', auth)

if __name__ == '__main__':
    main()
