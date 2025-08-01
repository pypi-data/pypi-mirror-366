#!/usr/bin/env python3
import sys, os, json, shutil, time
from remote_kernel import REMOTE_CONN_DIR, KERNELS_DIR, log, usage, version, __version__
from remote_kernel.ssh_wrapper import SSHConfig, SSHWrapper

def start_kernel(endpoint, conn_file, jump=None, python_bin="python"):
    if not os.path.exists(conn_file):
        log(f"ERROR: Connection file not found {conn_file}")
        return
    with open(conn_file) as f:
        cfg = json.load(f)
    ports = [cfg[k] for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]
    print(f"Starting remote kernel with ports: {ports}")
    ssh_cfg = SSHConfig(endpoint=endpoint, jump=jump)
    sshw = SSHWrapper(ssh_cfg)
    remote_conn_file = f"{REMOTE_CONN_DIR}/{os.path.basename(conn_file)}"
    if not sshw.copy(conn_file, remote_conn_file):
        log("Failed to copy connection file to remote host")
        return
    cmd = f"{python_bin} -m ipykernel_launcher -f {remote_conn_file}"
    print(f"Starting remote kernel with command: {cmd}")    
    out, err, success = sshw.exec_with_tunnels(cmd, ports)    
    if not success:
        log(f"Failed to start remote kernel: {err}")
    try:
        if os.path.exists(conn_file):
            os.remove(conn_file)
        sshw.exec(f"rm -f {remote_conn_file}")
    except Exception:
        pass
    log(f"Kernel exited, cleaning up remote file {remote_conn_file}")
    log(f"Kernel exited, cleaning up local file {conn_file}")
    time.sleep(5)

def add_kernel(endpoint, name, jump=None, python_bin=None):
    abs_path = sys.argv[0]
    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    os.makedirs(kernel_dir, exist_ok=True)
    argv = [abs_path, "--endpoint", endpoint, "-f", "{connection_file}"]
    if jump:
        argv += ["-J", jump]
    if python_bin:
        argv += ["--python", python_bin]
    kernel_json = {
        "argv": argv,
        "display_name": name,
        "language": "python"
    }
    with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
        json.dump(kernel_json, f, indent=2)
    log(f"Added kernel {name} ({endpoint})")
    log(f"Python: {python_bin}")
    log(f"Location: {kernel_dir}")

def list_kernels():
    """List kernels with endpoint, formatted as a clean table."""
    if not os.path.exists(KERNELS_DIR):
        log("No kernels installed")
        return

    print(f"{'slug':<10}| {'name':<15}| {'python':<15}| endpoint")
    print("-" * 80)
    for slug in os.listdir(KERNELS_DIR):
        kjson = os.path.join(KERNELS_DIR, slug, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        try:
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            python_bin = argv[argv.index("--python") + 1] if "--python" in argv else "python"
            if not endpoint:
                continue
            jump = argv[argv.index("-J") + 1] if "-J" in argv else None
            details = f"{endpoint}{f' -J {jump}' if jump else ''}"
            print(f"{slug:<10}| {name:<15}| {python_bin:<15}| {details}")
        except Exception as e:
            log(f"Failed to read kernel spec {kjson}: {e}")
    print("---")

def delete_kernel(name_or_slug):
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        log(f"Kernel '{name_or_slug}' not found")
        return
    try:
        shutil.rmtree(kernel_dir)
        log(f"Deleted kernel '{name_or_slug}'")
    except Exception as e:
        log(f"Failed to delete kernel '{name_or_slug}': {e}")

def find_target(name_or_slug):
    """Find the target kernel directory based on name or slug."""
    if not name_or_slug:
        list_kernels()
        log("Use: remote_kernel connect <slug-or-name>")
        return None
    target_slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, target_slug)
    kernel_json = os.path.join(kernel_dir, "kernel.json")
    if not os.path.exists(kernel_json):
        log(f"Kernel '{name_or_slug}' not found")
        return None
    try:
        with open(kernel_json) as f:
            data = json.load(f)
        argv = data.get("argv", [])
        endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
        jump = argv[argv.index("-J") + 1] if "-J" in argv else None
    except Exception as e:
        log(f"Failed to load kernel spec: {e}")
        return None
    if not endpoint:
        log(f"Kernel '{name_or_slug}' has no valid endpoint")
        return None
    log(f"Connecting to {endpoint}{f' -J {jump}' if jump else ''}...")
    ssh_cfg = SSHConfig(endpoint=endpoint, jump=jump)
    sshw = SSHWrapper(ssh_cfg)
    return sshw

def connect_kernel(name_or_slug=None):
    """Connect to a remote kernel interactively via SSHWrapper."""
    sshw = find_target(name_or_slug)
    if sshw:
        sshw.connect()
    return
    if not name_or_slug:
        list_kernels()
        log("Use: remote_kernel connect <slug-or-name>")
        return

    target_slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, target_slug)
    kernel_json = os.path.join(kernel_dir, "kernel.json")
    if not os.path.exists(kernel_json):
        log(f"Kernel '{name_or_slug}' not found")
        return

    try:
        with open(kernel_json) as f:
            data = json.load(f)
        argv = data.get("argv", [])
        endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
        jump = argv[argv.index("-J") + 1] if "-J" in argv else None
    except Exception as e:
        log(f"Failed to load kernel spec: {e}")
        return

    if not endpoint:
        log(f"Kernel '{name_or_slug}' has no valid endpoint")
        return

    log(f"Connecting to {endpoint}{f' -J {jump}' if jump else ''}...")
    ssh_cfg = SSHConfig(endpoint=endpoint, jump=jump)
    sshw = SSHWrapper(ssh_cfg)
    sshw.connect()

def sync_file(name_or_slug, src_file):
    """Sync a file to the remote host."""
    if not os.path.exists(src_file):
        log(f"Source file '{src_file}' does not exist")
        return
    sshw = find_target(name_or_slug)
    if sshw:
       remote_path = f"~/{os.path.basename(src_file)}"
    if sshw.copy(src_file, remote_path):
        log(f"File '{src_file}' synced to remote host at {remote_path}")
    else:
        log(f"Failed to sync file '{src_file}' to remote host")
    return

def main():
    if len(sys.argv) < 2 or "-h" in sys.argv or "--help" in sys.argv:
        usage()
        return
    if "-v" in sys.argv or "--version" in sys.argv:
        version()
        return

    first_cmd = sys.argv[1].lower()
    match first_cmd:
        case "run":
            pass
        case "add":
            if "--endpoint" not in sys.argv or "--name" not in sys.argv:
                usage()
                return
            endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
            name = sys.argv[sys.argv.index("--name") + 1]
            jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
            python_bin = sys.argv[sys.argv.index("--python") + 1] if "--python" in sys.argv else None        
            add_kernel(endpoint, name, jump, python_bin)
            return
        case "list":
            list_kernels()
            return
        case "delete":
            if len(sys.argv) < 3:
                usage()
                return
            delete_kernel(sys.argv[2])
            return            
        case "connect":
            target = sys.argv[2] if len(sys.argv) > 2 else None
            connect_kernel(target)
            return
        case "sync":
            target = sys.argv[2] if len(sys.argv) > 2 else None
            src_file = sys.argv[3] if len(sys.argv) > 3 else None
            sync_file(target, src_file)
            return
        case _:
            pass

    ## Start remote kernel
    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        usage()
        return    
    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
    python_bin = sys.argv[sys.argv.index("--python") + 1] if "--python" in sys.argv else "python"        
    start_kernel(endpoint, conn_file, jump, python_bin)
    return
    # end here
    if "add" in sys.argv:
        if "--endpoint" not in sys.argv or "--name" not in sys.argv:
            usage()
            return
        endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
        name = sys.argv[sys.argv.index("--name") + 1]
        jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
        python_bin = sys.argv[sys.argv.index("--python") + 1] if "--python" in sys.argv else None        
        add_kernel(endpoint, name, jump, python_bin)
        return
    if "list" in sys.argv:
        list_kernels()
        return
    if "delete" in sys.argv:
        if len(sys.argv) < 3:
            usage()
            return
        delete_kernel(sys.argv[2])
        return
    if "connect" in sys.argv:
        target = sys.argv[2] if len(sys.argv) > 2 else None
        connect_kernel(target)
        return
    
    ## Start remote kernel
    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        usage()
        return    
    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
    python_bin = sys.argv[sys.argv.index("--python") + 1] if "--python" in sys.argv else "python"        
    start_kernel(endpoint, conn_file, jump, python_bin)

if __name__ == "__main__":
    main()