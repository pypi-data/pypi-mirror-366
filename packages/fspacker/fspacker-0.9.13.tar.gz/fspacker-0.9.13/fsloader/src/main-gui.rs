#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod utils;

#[cfg(feature = "gui")]
fn main() {
    let entry_files = utils::find_entry_files();
    if 0 == entry_files.len() {
        println!("未找到入口脚本文件");
        return;
    }

    for file in entry_files {
        println!("正在执行脚本: {}", file);
        utils::run_python_script(&file);
    }
}
