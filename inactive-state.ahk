;#SingleInstance Force

TraySetIcon("inactive.ico")

;*SC01F::
;{
;	If ((GetKeyState("LAlt","p") || GetKeyState("RAlt","p"))) {
;		If ((GetKeyState("RWin","p") || GetKeyState("LWin","p"))) {
;			iniPath := A_ScriptDir "\config.ini"
;			fromFile := IniRead(iniPath, "Inactive-state", "From", "")
;
;			path := fromFile
;			Run path
;			ExitApp
;
;		}
;	}
;	else {
;		Send "{blind}{s}"
;	}
;}

#!SC01F::
{
	config := A_ScriptDir . "\config.ini"
	If GetKeyState("s","p") {
		iniPath := A_ScriptDir "\config.ini"
		If (A_IsCompiled) {
			Istate := "Inactive-state-compiled"
		} else {
			Istate := "Inactive-state-not-compiled"
		}
		fromFile := IniRead(iniPath, Istate, "From", "")

		path := fromFile
		Run path
		IniWrite("Activated AHK", config, "LettersOverlay", "Message")
		Run (A_ScriptDir . "\labelWidget.pyw Activated")
		ExitApp
	}
	else {
		Send "{blind}{s}"
	}
}

