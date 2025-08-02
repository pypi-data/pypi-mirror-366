use std::fs;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process::{Command, Stdio};

pub fn find_entry_files() -> Vec<String> {
    let current_dir = Path::new(".");
    let mut entry_files = Vec::new();

    if let Ok(entries) = fs::read_dir(current_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_file() && path.extension().and_then(|e| e.to_str()) == Some("int") {
                    entry_files.push(path.to_string_lossy().into_owned());
                }
            }
        }
    }
    entry_files
}

pub fn run_python_script(script_path: &str) {
    let python_path = if cfg!(target_os = "windows") {
        if cfg!(feature = "gui") {
            Path::new("runtime/pythonw.exe")
        } else {
            Path::new("runtime/python.exe")
        }
    } else {
        if cfg!(feature = "gui") {
            Path::new("runtime/pythonw")
        } else {
            Path::new("runtime/python")
        }
    };

    let mut command = Command::new(python_path);
    command.arg(script_path);

    // 仅 Windows 需要特殊处理
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        // 设置 CREATE_NO_WINDOW 标志
        command.creation_flags(0x08000000);
    }

    let mut child = Command::new(python_path) // 或指定绝对路径如 "runtime/python.exe"
        .arg(script_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("启动Python失败");

    // 异步读取输出流
    let stdout = BufReader::new(child.stdout.take().unwrap());
    let stderr = BufReader::new(child.stderr.take().unwrap());

    // 配置日志
    let log_file = fs::File::create("output.log").unwrap();
    command.stdout(Stdio::from(log_file.try_clone().unwrap()));
    command.stderr(Stdio::from(log_file));

    // 输出处理线程
    let handle = std::thread::spawn(move || {
        for line in stdout.lines() {
            println!("输出: {}", line.unwrap());
        }
        for line in stderr.lines() {
            eprintln!("错误: {}", line.unwrap());
        }
    });

    let _status = child.wait().expect("进程未正常退出");
    handle.join().unwrap();
}
