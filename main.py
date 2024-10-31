import sys
import os
import scp

def main(args: list[str]):
    """
    Command-line arguments:
    0: acme root folder path
    1: base_domains to iterate over, split by comma (,)
    2: targets to send certs to, split by comma (,)
    3: temp_cert_dir
    """
    acme_root = os.path.normpath(args[0])
    base_domains = args[1].split(",")
    targets_unparsed = args[2].split(",")
    temp_cert_dir = os.path.normpath(args[3])

    domains = get_domains(acme_root, base_domains)
    copy_jobs = parse_targets(targets_unparsed, temp_cert_dir)

    create_pems(acme_root, domains, temp_cert_dir)
    #TODO: Test copy()
    #copy(copy_jobs)

def copy(copy_jobs: list[dict]):
    for job in copy_jobs:
        client = scp.Client(host=job["server"], user=job["user"])
        client.use_system_keys()
        client.transfer(job["source"], job["destination"])


def create_pems(acme_root: str, domains: list[str], temp_cert_dir: str):
    if not os.path.exists(temp_cert_dir):
        os.makedirs(temp_cert_dir)

    for domain in domains:
        os.remove(temp_cert_dir + "/" + domain + ".pem")
        with open(acme_root + "/" + domain + "_ecc/" + domain + ".key",'r') as keyfile, open(temp_cert_dir + "/" + domain + ".pem",'a') as pemfile: 
            for line in keyfile: 
                pemfile.write(line)
            pemfile.write("\n")
        with open(acme_root + "/" + domain + "_ecc/" + "fullchain.cer",'r') as certfile, open(temp_cert_dir + "/" + domain + ".pem",'a') as pemfile: 
            for line in certfile: 
                pemfile.write(line)

def get_domains(acme_root, base_domains) -> list[str]:
    domains = []
    subfolders = os.walk(acme_root)
    for base_domain in base_domains:
        for folder in subfolders:
            if base_domain in folder[0]:
                domains.append(folder[0].split("/")[-1].split("_ecc")[0])
    return domains

def parse_targets(targets_unparsed: list[str], temp_cert_dir: str) -> list[dict]:
    """
    Example targets_unparsed: ['*>user@server.local:/certs/', 'wings01.chri.no_ecc/wings01.chri.no.key;simon@wings01.dmz.chri.no:/certs/']
    """
    copy_jobs = []
    for target in targets_unparsed:
        if target.split(";")[0] == "*":
            copy_jobs.append({
                "source": temp_cert_dir + "/*",
                "user": target.split(";")[1].split("@")[0],
                "server": target.split(";")[1].split("@")[1].split(":")[0],
                "destination": target.split(";")[1].split("@")[1].split(":")[1]
            })
        else:
            copy_jobs.append({
                "source": target.split(";")[0],
                "user": target.split(";")[1].split("@")[0],
                "server": target.split(";")[1].split("@")[1].split(":")[0],
                "dir": target.split(";")[1].split("@")[1].split(":")[1]
            })
    
    return copy_jobs

if __name__ == "__main__":
    main(sys.argv[1:])
