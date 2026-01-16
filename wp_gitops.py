#!/usr/bin/env python3
"""
WordPress GitOps Sync Tool - MVP
Synkronoi WordPress-teemat, pluginit ja konfiguraatiot Gitin kanssa
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


class WordPressGitOps:
    def __init__(self, wp_path, git_repo_path, verbose=False):
        self.wp_path = Path(wp_path)
        self.git_repo = Path(git_repo_path)
        self.backup_dir = self.git_repo / "backups"
        self.config_file = self.git_repo / "wp-gitops-config.json"
        self.verbose = verbose
        
        # Tarkista että polut ovat valideja
        if not self.wp_path.exists():
            raise ValueError(f"WordPress-polku ei löydy: {wp_path}")
        
        if not self.git_repo.exists():
            self.git_repo.mkdir(parents=True, exist_ok=True)
            self._init_git_repo()
        
        self.backup_dir.mkdir(exist_ok=True)
        self._load_config()
    
    def _init_git_repo(self):
        """Alusta Git-repositorio jos ei ole olemassa"""
        if not (self.git_repo / ".git").exists():
            subprocess.run(["git", "init"], cwd=self.git_repo, check=True, 
                         capture_output=not self.verbose)
            if self.verbose:
                print(f"✓ Git-repositorio alustettu: {self.git_repo}")
    
    def _load_config(self):
        """Lataa tai luo konfiguraatio"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "sync_themes": True,
                "sync_plugins": True,
                "sync_uploads": False,  # Oletuksena pois, voi olla iso
                "excluded_plugins": ["akismet", "hello"],  # Esimerkkejä
                "last_sync": None
            }
            self._save_config()
    
    def _save_config(self):
        """Tallenna konfiguraatio"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _create_backup(self, name):
        """Luo varmuuskopio ennen muutoksia"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{name}_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        return backup_path
    
    def _run_git_command(self, command):
        """Suorita Git-komento"""
        try:
            result = subprocess.run(
                command,
                cwd=self.git_repo,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Git-virhe: {e.stderr}")
            return None
    
    def sync_to_git(self, message=None, dry_run=False):
        """Synkronoi WordPress → Git"""
        print("\n🔄 Synkronoidaan WordPress → Git...")
        
        if dry_run:
            print("⚠️  DRY RUN - ei tehdä oikeita muutoksia\n")
        
        changes = []
        file_count = 0
        
        # Synkronoi teemat
        if self.config["sync_themes"]:
            themes_src = self.wp_path / "wp-content" / "themes"
            themes_dst = self.git_repo / "themes"
            
            if themes_src.exists():
                if not dry_run:
                    if themes_dst.exists():
                        shutil.rmtree(themes_dst)
                    shutil.copytree(themes_src, themes_dst, 
                                  ignore=shutil.ignore_patterns('*.log', 'node_modules'))
                
                # Laske teemat
                theme_count = len([d for d in themes_src.iterdir() if d.is_dir()])
                changes.append(f"{theme_count} teemaa")
                if self.verbose:
                    print(f"✓ Teemat kopioitu: {themes_dst}")
        
        # Synkronoi pluginit
        if self.config["sync_plugins"]:
            plugins_src = self.wp_path / "wp-content" / "plugins"
            plugins_dst = self.git_repo / "plugins"
            
            if plugins_src.exists():
                if not dry_run:
                    if plugins_dst.exists():
                        shutil.rmtree(plugins_dst)
                    plugins_dst.mkdir(exist_ok=True)
                    
                    # Kopioi vain halutut pluginit
                    for plugin in plugins_src.iterdir():
                        if plugin.name not in self.config["excluded_plugins"]:
                            dst_plugin = plugins_dst / plugin.name
                            if plugin.is_dir():
                                shutil.copytree(plugin, dst_plugin,
                                              ignore=shutil.ignore_patterns('*.log', 'node_modules'))
                            else:
                                shutil.copy2(plugin, dst_plugin)
                            file_count += 1
                
                plugin_count = len([p for p in plugins_src.iterdir() 
                                  if p.name not in self.config["excluded_plugins"]])
                changes.append(f"{plugin_count} pluginia")
                if self.verbose:
                    print(f"✓ Pluginit kopioitu: {plugins_dst}")
        
        if not dry_run and changes:
            # Commit muutokset Gitiin
            self._run_git_command(["git", "add", "."])
            
            commit_msg = message or f"Sync: {', '.join(changes)}"
            self._run_git_command(["git", "commit", "-m", commit_msg])
            
            self.config["last_sync"] = datetime.now().isoformat()
            self._save_config()
            
            print(f"✅ Synkronoitu: {', '.join(changes)}")
            if self.verbose:
                print(f"   Commit: {commit_msg}")
        elif dry_run:
            print(f"📋 Synkronoitaisiin: {', '.join(changes)}")
        else:
            print("\nℹ️  Ei muutoksia synkronoitavaksi")
    
    def sync_from_git(self, dry_run=False):
        """Synkronoi Git → WordPress"""
        print("\n🔄 Synkronoidaan Git → WordPress...")
        
        if dry_run:
            print("⚠️  DRY RUN - ei tehdä oikeita muutoksia\n")
        
        synced_items = []
        
        # Luo varmuuskopio ensin
        if not dry_run:
            backup = self._create_backup("pre_sync")
            if self.verbose:
                print(f"✓ Varmuuskopio luotu: {backup}")
        
        # Synkronoi teemat
        if self.config["sync_themes"]:
            themes_src = self.git_repo / "themes"
            themes_dst = self.wp_path / "wp-content" / "themes"
            
            if themes_src.exists():
                theme_count = 0
                if not dry_run:
                    # Älä poista kaikkea, päivitä vain Git-repossa olevat
                    for theme in themes_src.iterdir():
                        # Ohita tiedostot kuten index.php, synkronoi vain hakemistot
                        if not theme.is_dir():
                            continue
                            
                        dst_theme = themes_dst / theme.name
                        if dst_theme.exists():
                            shutil.rmtree(dst_theme)
                        shutil.copytree(theme, dst_theme)
                        theme_count += 1
                else:
                    theme_count = len([d for d in themes_src.iterdir() if d.is_dir()])
                
                synced_items.append(f"{theme_count} teemaa")
        
        # Synkronoi pluginit
        if self.config["sync_plugins"]:
            plugins_src = self.git_repo / "plugins"
            plugins_dst = self.wp_path / "wp-content" / "plugins"
            
            if plugins_src.exists():
                plugin_count = 0
                if not dry_run:
                    for plugin in plugins_src.iterdir():
                        dst_plugin = plugins_dst / plugin.name
                        if dst_plugin.exists():
                            if dst_plugin.is_dir():
                                shutil.rmtree(dst_plugin)
                            else:
                                dst_plugin.unlink()
                        
                        if plugin.is_dir():
                            shutil.copytree(plugin, dst_plugin)
                        else:
                            shutil.copy2(plugin, dst_plugin)
                        plugin_count += 1
                else:
                    plugin_count = len(list(plugins_src.iterdir()))
                
                synced_items.append(f"{plugin_count} pluginia")
        
        if not dry_run:
            print(f"✅ Synkronoitu WordPressiin: {', '.join(synced_items)}")
        else:
            print(f"📋 Synkronoitaisiin: {', '.join(synced_items)}")
    
    def status(self):
        """Näytä tilanne"""
        print("\n📊 WordPress GitOps - Tilanne\n")
        print(f"WordPress-polku: {self.wp_path}")
        print(f"Git-repositorio: {self.git_repo}")
        print(f"Viimeisin synkronointi: {self.config.get('last_sync', 'Ei koskaan')}")
        print(f"\nAsetukset:")
        print(f"  - Synkronoi teemat: {self.config['sync_themes']}")
        print(f"  - Synkronoi pluginit: {self.config['sync_plugins']}")
        print(f"  - Synkronoi uploads: {self.config['sync_uploads']}")
        print(f"  - Poissuljetut pluginit: {', '.join(self.config['excluded_plugins'])}")
        
        # Git-tila
        git_status = self._run_git_command(["git", "status", "--short"])
        if git_status:
            print(f"\nGit-muutokset:\n{git_status}")
        else:
            print("\nGit: Ei committoimattomia muutoksia")
    
    def diff(self):
        """Näytä erot Git-repon ja WordPressin välillä"""
        print("\n🔍 Vertaillaan eroja...\n")
        
        # Yksinkertainen vertailu teemojen osalta
        if self.config["sync_themes"]:
            wp_themes = set(p.name for p in (self.wp_path / "wp-content" / "themes").iterdir() if p.is_dir())
            git_themes = set(p.name for p in (self.git_repo / "themes").iterdir() if p.is_dir()) if (self.git_repo / "themes").exists() else set()
            
            print("Teemat:")
            only_wp = wp_themes - git_themes
            only_git = git_themes - wp_themes
            both = wp_themes & git_themes
            
            if only_wp:
                print(f"  Vain WordPressissä: {', '.join(only_wp)}")
            if only_git:
                print(f"  Vain Gitissä: {', '.join(only_git)}")
            if both:
                print(f"  Molemmissa: {', '.join(both)}")


def main():
    parser = argparse.ArgumentParser(description="WordPress GitOps Sync Tool")
    parser.add_argument("--wp-path", required=True, help="WordPress-asennuksen polku")
    parser.add_argument("--git-repo", required=True, help="Git-repositorion polku")
    parser.add_argument("-v", "--verbose", action="store_true", help="Näytä yksityiskohtaiset tiedot")
    
    subparsers = parser.add_subparsers(dest="command", help="Komennot")
    
    # Sync to Git
    sync_to_parser = subparsers.add_parser("push", help="Synkronoi WordPress → Git")
    sync_to_parser.add_argument("-m", "--message", help="Commit-viesti")
    sync_to_parser.add_argument("--dry-run", action="store_true", help="Simuloi ilman muutoksia")
    
    # Sync from Git
    sync_from_parser = subparsers.add_parser("pull", help="Synkronoi Git → WordPress")
    sync_from_parser.add_argument("--dry-run", action="store_true", help="Simuloi ilman muutoksia")
    
    # Status
    subparsers.add_parser("status", help="Näytä tilanne")
    
    # Diff
    subparsers.add_parser("diff", help="Näytä erot")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        gitops = WordPressGitOps(args.wp_path, args.git_repo, verbose=args.verbose)
        
        if args.command == "push":
            gitops.sync_to_git(message=args.message, dry_run=args.dry_run)
        elif args.command == "pull":
            gitops.sync_from_git(dry_run=args.dry_run)
        elif args.command == "status":
            gitops.status()
        elif args.command == "diff":
            gitops.diff()
    
    except Exception as e:
        print(f"\n❌ Virhe: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
