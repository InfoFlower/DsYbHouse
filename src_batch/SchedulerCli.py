import cmd
from TaskRegistery import Registery
from dataclasses import asdict        
MyRegistery = Registery()


class MonInteractif(cmd.Cmd):
    intro = "Bienvenue dans l'application interactive. Tapez ? pour les commandes."
    prompt = "> "
    
    def do_run_task(self, arg):
        """Joue une tache"""
        if len(arg)>0:
            task = arg[0]
            print(task)
        else :
            print('Please specify task to_run')

    def do_show_tasks(self, arg):
        """Montre les taches courantes"""
        print(MyRegistery.make_frame())
        
    def do_save_tasks(self, arg):
        MyRegistery.write_json()

    # Permet aussi de quitter avec Ctrl+D
    def do_EOF(self, arg):
        """Ctrl + D"""
        return True

if __name__ == "__main__":

    MonInteractif().do_show_tasks('')