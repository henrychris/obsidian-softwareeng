
import os
import re

def get_all_files(root_dir):
    all_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            all_files.append(os.path.join(dirpath, filename))
    return all_files

def create_filename_to_path_map(all_files):
    file_map = {}
    for fpath in all_files:
        filename = os.path.basename(fpath)
        file_map[filename] = fpath
        # Also add the full path as a key, in case links are already relative paths
        file_map[fpath] = fpath
        # Add path without extension for markdown files
        if fpath.endswith(".md"):
            file_map[os.path.splitext(filename)[0]] = fpath
        # Add path relative to root for easier lookup
        file_map[os.path.relpath(fpath, os.getcwd())] = fpath
        if fpath.endswith(".md"):
            file_map[os.path.splitext(os.path.relpath(fpath, os.getcwd()))[0]] = fpath
    return file_map

def get_relative_path(from_path, to_path):
    return os.path.relpath(to_path, os.path.dirname(from_path))

def update_links_in_file(filepath, file_map, root_dir):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = content
    # Regex to find Obsidian links: [[link_target|display_text]] or [[link_target]]
    # Group 1: link_target, Group 2: display_text (optional), Group 3: heading (optional)
    link_pattern = re.compile(r'\[\[([^\]\|#]+)(?:#([^\]\|]+))?(?:\|([^\]]+))?\]\]')

    for match in link_pattern.finditer(content):
        link_target = match.group(1)
        heading = match.group(2)
        display_text = match.group(3)
        full_match = match.group(0)

        resolved_path = None
        
        # Try to resolve the link target to a new absolute path
        # 1. Try exact match (including relative paths from root)
        if link_target in file_map:
            resolved_path = file_map[link_target]
        elif link_target + '.md' in file_map: # Try with .md extension
            resolved_path = file_map[link_target + '.md']
        elif os.path.basename(link_target) in file_map: # Try just the basename
            resolved_path = file_map[os.path.basename(link_target)]
        elif os.path.basename(link_target) + '.md' in file_map:
            resolved_path = file_map[os.path.basename(link_target) + '.md']
        
        # Handle relative paths in link_target
        if not resolved_path and (link_target.startswith('./') or link_target.startswith('../') or '/' in link_target):
            abs_link_target = os.path.normpath(os.path.join(os.path.dirname(filepath), link_target))
            if abs_link_target in file_map.values():
                resolved_path = abs_link_target
            elif abs_link_target + '.md' in file_map.values():
                resolved_path = abs_link_target + '.md'
            else:
                # Try to find it in the map by its full path relative to root
                relative_to_root_link_target = os.path.relpath(abs_link_target, root_dir)
                if relative_to_root_link_target in file_map:
                    resolved_path = file_map[relative_to_root_link_target]
                elif relative_to_root_link_target + '.md' in file_map:
                    resolved_path = file_map[relative_to_root_link_target + '.md']

        if resolved_path:
            new_relative_path = get_relative_path(filepath, resolved_path)
            
            # Determine if it's an image or markdown file
            if resolved_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # For images, ensure the link starts with ![[ and keeps the extension
                new_link = f"![[{new_relative_path}"
                if display_text:
                    new_link += f"|{display_text}"
                new_link += "]]"
            else:
                # For markdown files, remove .md extension from the link target
                if new_relative_path.endswith('.md'):
                    new_relative_path = new_relative_path[:-3]
                
                new_link = f"[[{new_relative_path}"
                if heading:
                    new_link += f"#{heading}"
                if display_text:
                    new_link += f"|{display_text}"
                new_link += "]]"
            
            # Only replace if the link has actually changed
            if new_link != full_match:
                updated_content = updated_content.replace(full_match, new_link)
        else:
            print(f"Warning: Could not resolve link target '{link_target}' in file '{filepath}'")

    if updated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated links in: {filepath}")
    else:
        print(f"No changes needed for: {filepath}")

if __name__ == "__main__":
    root_directory = os.getcwd()
    all_files = get_all_files(root_directory)
    filename_to_path_map = create_filename_to_path_map(all_files)

    for md_file in [f for f in all_files if f.endswith(".md")]:
        update_links_in_file(md_file, filename_to_path_map, root_directory)
