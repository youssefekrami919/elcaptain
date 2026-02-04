import os, time, socket, subprocess
from core.config import RUN_WITH_DOCKER, NEO4J_DOCKER_CONTAINER, NEO4J_DOCKER_HTTP_PORT, NEO4J_DOCKER_BOLT_PORT, NEO4J_DOCKER_PASSWORD

def port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def run_cmd(cmd: list[str]) -> tuple[int,str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()

def ensure_neo4j_docker():
    if port_open("127.0.0.1", NEO4J_DOCKER_BOLT_PORT):
        print(f"Neo4j already running on bolt:{NEO4J_DOCKER_BOLT_PORT}")
        return

    code, _ = run_cmd(["docker","--version"])
    if code != 0:
        raise RuntimeError("Docker not available. Install Docker Desktop OR start Neo4j manually then run: streamlit run app.py")

    code, out = run_cmd(["docker","ps","-a","--format","{{.Names}}"])
    if code != 0:
        raise RuntimeError(out)
    names=set([x.strip() for x in out.splitlines() if x.strip()])

    if NEO4J_DOCKER_CONTAINER in names:
        print(f"Starting container {NEO4J_DOCKER_CONTAINER}...")
        code,out = run_cmd(["docker","start",NEO4J_DOCKER_CONTAINER])
        if code != 0: raise RuntimeError(out)
    else:
        print(f"Creating container {NEO4J_DOCKER_CONTAINER}...")
        code,out = run_cmd([
            "docker","run","-d","--name",NEO4J_DOCKER_CONTAINER,
            "-p",f"{NEO4J_DOCKER_HTTP_PORT}:7474",
            "-p",f"{NEO4J_DOCKER_BOLT_PORT}:7687",
            "-e",f"NEO4J_AUTH=neo4j/{NEO4J_DOCKER_PASSWORD}",
            "neo4j:5"
        ])
        if code != 0: raise RuntimeError(out)

    print("Waiting for Neo4j Bolt...")
    for _ in range(60):
        if port_open("127.0.0.1", NEO4J_DOCKER_BOLT_PORT):
            print("Neo4j is ready.")
            return
        time.sleep(1)
    raise RuntimeError("Neo4j did not become ready. Check: docker logs " + NEO4J_DOCKER_CONTAINER)

def main():
    if RUN_WITH_DOCKER:
        ensure_neo4j_docker()
        print(f"Neo4j Browser: http://localhost:{NEO4J_DOCKER_HTTP_PORT}")
        print(f"Neo4j Bolt: neo4j://localhost:{NEO4J_DOCKER_BOLT_PORT}")
        print("Set these in .env:")
        print(f"  NEO4J_URI=neo4j://localhost:{NEO4J_DOCKER_BOLT_PORT}")
        print("  NEO4J_USER=neo4j")
        print(f"  NEO4J_PASSWORD={NEO4J_DOCKER_PASSWORD}")
    os.execvp("python", ["python","-m","streamlit","run","app.py"])

if __name__ == "__main__":
    main()
