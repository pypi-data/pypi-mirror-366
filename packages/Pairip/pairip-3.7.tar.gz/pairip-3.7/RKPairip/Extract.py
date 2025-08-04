from .C_M import CM; C = CM()

def Extract_Smali(decompile_dir, smali_folders, L_S_F, isAPKTool):

    Extract_Dir = C.os.path.join(decompile_dir, *(['smali_classes'] if isAPKTool else ['smali', 'classes']))

    Target_Regex = C.re.compile(r'\.class public L([^;]+);\n\.super Ljava/lang/Object;\s+# static fields\n\.field public static [^: ]+:Ljava/lang/String;\n')

    App_Smali = C.os.path.join("com", "pairip", "application", "Application.smali")

    Smali_Files = []; folder_suffix = 2; Pairip_Smali = 0
    Move_Pairip_Smali = set(); Move_App_Smali = False
    
    while C.os.path.exists(f"{Extract_Dir}{folder_suffix}"):
        folder_suffix += 1
    Extract_Dir = f"{Extract_Dir}{folder_suffix}"
    C.os.makedirs(Extract_Dir, exist_ok=True)

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Extract Smali {C.rkj}➸❥ {C.g}{C.os.path.basename(Extract_Dir)}")

    for smali_folder in smali_folders:
        for root, _, files in C.os.walk(smali_folder):
            for file in files:
                if file.endswith(".smali"):
                    Smali_Files.append(C.os.path.join(root, file))

    for Smali_File in Smali_Files:
        if Smali_File.endswith(App_Smali) and not Move_App_Smali:
            Relative_Path = App_Smali
            Move_App_Smali = True
        else:
            Smali = open(Smali_File, 'r', encoding='utf-8', errors='ignore').read()
            match = Target_Regex.search(Smali)
            if match:
                Relative_Path = match[1].replace("/", C.os.sep) + ".smali"
                if Relative_Path not in Move_Pairip_Smali:
                    Pairip_Smali += 1
                    Move_Pairip_Smali.add(Relative_Path)
                else: continue
            else: continue

        Target_Path = C.os.path.join(Extract_Dir, Relative_Path)
        C.os.makedirs(C.os.path.dirname(Target_Path), exist_ok=True)
        C.shutil.move(Smali_File, Target_Path)

        print(f"{C.g}  |\n  └──── {C.r} Move ~{C.g}$ {C.y}{C.os.path.basename(Smali_File)} {C.g}✔")
    print(f"\n\n{C.lb}[ {C.c}Moved {C.lb}] {C.rkj}➸❥ {C.pr}1 {C.g}Application Smali ✔")
    print(f"\n{C.lb}[ {C.c}Moved {C.lb}] {C.rkj}➸❥ {C.pr}{Pairip_Smali} {C.g}Pairip Smali ✔")
    print(f"\n{C.r}{'_' * 61}\n")

# Logs_Injected
def Logs_Injected(L_S_F):
    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Last Smali Folder {C.g}➸❥ {C.y}{C.os.path.basename(L_S_F)} {C.g}✔\n")
    print(f"\n{C.lb}[ {C.cp}* {C.lb}] {C.c} Logs Inject in Target SMALI")
    Class_Names = []; Last_Smali_Path = None
    Sequence = 1; Logs_Inject = 0
        
    for root, _, files in C.os.walk(L_S_F):
        for file in files:
            path = C.os.path.join(root, file)
            content = open(path, 'r', encoding='utf-8', errors='ignore').read()

            Class_Match = C.re.search(r'\.class public L([^;]+);', content)
            Static_Fields = C.re.findall(r'\.field public static ([^: ]+):Ljava/lang/String;\n', content)

            if Class_Match and Static_Fields:
                Class_Names.append(Class_Match[1])
                content = C.re.sub(r'(\.super Ljava/lang/Object;)', rf'\1\n.source "{Sequence:1d}.java"', content)

                log_method = ['.method public static FuckUByRK()V', '    .registers 2']
                for i, field in enumerate(Static_Fields):
                    log_method += [
                        f'    sget-object v0, L{Class_Match[1]};->{field}:Ljava/lang/String;',
                        f'    const-string v1, "{Sequence:1d}.java:{i+1}"',
                        f'    .line {i+1}',
                        f'    .local v0, "{Sequence:1d}.java:{i+1}":V',
                        f'    invoke-static {{v0}}, LRK_TECHNO_INDIA/ObjectLogger;->logstring(Ljava/lang/Object;)V',
                        f'    sput-object v0, L{Class_Match[1]};->{field}:Ljava/lang/String;'
                    ]
                log_method += ['    return-void', '.end method']
                content += '\n' + '\n'.join(log_method)

                open(path, 'w', encoding='utf-8', errors='ignore').write(content)

                print(f"{C.g}  |\n  └──── {C.r}Logs Inject ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(path)}{C.g} ✔")
                Last_Smali_Path = path; Sequence += 1; Logs_Inject += 1

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Logs Injected {C.rkj}➸❥ {C.pr}{Logs_Inject} {C.g}✔\n")

    if Class_Names and Last_Smali_Path:
        print(f'\n{C.lb}[ {C.cp}* {C.lb}] {C.c} Added Callobjects Method\n')

        code = ('\n.method public static callobjects()V\n\t'
                '.registers 2\n\t' +
                ''.join(f'invoke-static {{}}, L{CN};->FuckUByRK()V\n\t' for CN in Class_Names) +
                'return-void\n.end method\n')

        open(Last_Smali_Path, 'a', encoding='utf-8', errors='ignore').write(code)

        print(f"{C.g}  |\n  └──── {C.r}Target Smali ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(Last_Smali_Path)}{C.g} ✔\n")

    H_App_Smali = C.os.path.join(L_S_F, 'com', 'pairip', 'application', 'Application.smali')

    if Last_Smali_Path and C.os.path.exists(H_App_Smali):
        print(f'\n{C.lb}[ {C.cp}* {C.lb}] {C.c} Hook Callobjects Method\n')
        C_Name = C.os.path.splitext(C.os.path.relpath(Last_Smali_Path, L_S_F).replace(C.os.sep, "/"))[0]

        content = open(H_App_Smali, 'r', encoding='utf-8', errors='ignore').read()

        Hook_Callobjects = C.re.sub(r'(\.method public constructor <init>\(\)V[\s\S]*?)(\s+return-void\n.end method)', rf'\1\n\tinvoke-static {{}}, L{C_Name};->callobjects()V\n\2', content)

        open(H_App_Smali, 'w', encoding='utf-8', errors='ignore').write(Hook_Callobjects)

        print(f"{C.g}  |\n  └──── {C.r}Target Smali ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(H_App_Smali)}{C.g} ✔\n")

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Patching Done {C.g}✔\n")
    print(f"{C.r}{'_' * 61}\n")