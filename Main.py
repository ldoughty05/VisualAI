# 6/3/2022 Project day 4

import tkinter as tk
import Placeables
import Constants as Const

rclickCanvasPos = (0, 0)  # global variables like this are discouraged. Make it into a class and save as instance?
lastLeftClickCanvasPos = (0, 0)
inspectorFocus = None
objectsArr = []


def pan_start(event):
    canvas.scan_mark(event.x, event.y)


def pan_move(event):
    canvas.scan_dragto(event.x, event.y, gain=1)


def do_popupMenu(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()
        global rclickCanvasPos
        rclickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))


def createGridLines(sizeX, sizeY, gridSpacing):
    for x in range(int(sizeX / gridSpacing)):  # vertical lines
        canvas.create_line(x * gridSpacing, 0, x * gridSpacing, sizeY, width=1, fill=Const.COL_C)
    for y in range(int(sizeY / gridSpacing)):  # vertical lines
        canvas.create_line(0, y * gridSpacing, sizeX, y * gridSpacing, width=1, fill=Const.COL_C)


def createCircle(canv, x, y, r, **kwargs):
    return canv.create_oval(x + r, y + r, x - r, y - r, kwargs)


def addPlaceableToList(placeable):
    objListBox.insert('end', placeable.name)
    if len(objectsArr) % 2 == 1:
        objListBox.itemconfig(objListBox.size() - 1, bg=Const.COL_Bl)


def addCircle():  # DEPRECIATED
    global objectsArr
    circle = Placeables.Solo(rclickCanvasPos[0], rclickCanvasPos[1], Const.NODE_RADIUS)
    circle.drawing = (createCircle(canvas, circle.x, circle.y, circle.radius * 1.8, fill=circle.tabcolor,
                                   outline=circle.tabOutlineCol, width=2, tags=('inspectable', 'draggable')),
                      createCircle(canvas, circle.x, circle.y, circle.radius, fill=circle.color, width=0,
                                   tags='inspectable'))
    objectsArr.append(circle)
    addPlaceableToList(circle)


def addLayerBlock():
    spacing = Const.NODE_RADIUS * 1.5
    global objectsArr
    box = Placeables.LayerBlock(rclickCanvasPos[0], rclickCanvasPos[1], 5)
    tdrawlist = [canvas.create_rectangle(box.bound.x0, box.bound.y0, box.bound.x1, box.bound.y1,  # draw box
                                         fill=box.color, outline=box.outlineCol, width=2,
                                         tags=('inspectable', 'draggable'))]
    for n in range(box.size):  # draw nodes
        tdrawlist.append(createCircle(canvas, box.nodes[n].x, box.nodes[n].y, Const.NODE_RADIUS,
                                      fill=box.ncolor, width=0, tags=('inspectable', 'linkable')))
    box.drawing = tuple(tdrawlist)
    objectsArr.append(box)
    addPlaceableToList(box)


def selectPlaceable(event):
    # on B1 down # doesn't consistenty register when clicking. Bug might be somewhere else. Boundbox
    # doesnt drag properly?
    print('placeableEvent')
    global lastLeftClickCanvasPos
    lastLeftClickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))


def dragPlaceable(event):  # on B1 motion
    global lastLeftClickCanvasPos
    if not isinstance(inspectorFocus, Placeables.Placeable):
        return
    if isinstance(inspectorFocus.drawing, tuple):
        for e in inspectorFocus.drawing:
            canvas.move(e, canvas.canvasx(event.x) - lastLeftClickCanvasPos[0],
                        canvas.canvasy(event.y) - lastLeftClickCanvasPos[1])
    else:
        canvas.move(inspectorFocus.drawing, canvas.canvasx(event.x) - lastLeftClickCanvasPos[0],
                    canvas.canvasy(event.y) - lastLeftClickCanvasPos[1])
    inspectorFocus.x = inspectorFocus.x + canvas.canvasx(event.x) - lastLeftClickCanvasPos[0]
    inspectorFocus.y = inspectorFocus.y + canvas.canvasy(event.y) - lastLeftClickCanvasPos[1]
    lastLeftClickCanvasPos = (canvas.canvasx(event.x), canvas.canvasy(event.y))


def forgetPlaceable(event):  # on B1 up  # May be unnecessary
    refreshInspector()


def setInspectorFocus(event):
    print("inspectorFocusEvent")
    global inspectorFocus
    if inspectorFocus is not None:  # last inspectorFocus
        canvas.itemconfig(inspectorFocus.drawing[0], outline='white')
    for p in reversed(objectsArr):  # last to first in list
        if p.bound.w <= canvas.canvasx(event.x) <= p.bound.e and p.bound.n <= canvas.canvasy(event.y) <= p.bound.s:
            inspectorFocus = p
            canvas.itemconfig(inspectorFocus.drawing[0], outline=Const.COL_HI)
            break
    refreshInspector()


def refreshInspector():
    if len(inspector.winfo_children()) > 1:
        print('multiple windows in inspector')
    inspector.winfo_children()[0].destroy()  # destroys last inspBox
    inspBox = tk.Frame(inspector, bg=Const.COL_A)
    inspBox.place(width=inspector.winfo_width() - 20, x=10, relheight=1)
    for attr, value in inspectorFocus.__dict__.items():
        lnfr = tk.Frame(inspBox, bg=Const.COL_A, bd=0, relief='sunken')
        lnfr.pack(fill='x')
        lab = tk.Label(lnfr, bg=Const.COL_A, bd=0, fg='white', text=f'{attr} :  ', padx=0, pady=5)
        lab.pack(side='left')
        entry = tk.Entry(lnfr, bg=Const.COL_Bl, bd=1, fg='white')
        entry.pack(expand=True, side='left', fill='x')
        if value is not None:
            entry.insert('end', value)
        entry.configure(state='disabled', disabledbackground=Const.COL_A, disabledforeground='white')


def setLinkEnd(event):
    print('\\linkEndEvent')
    for end in reversed(objectsArr):  # last to first in list
        if isinstance(end, Placeables.LayerBlock) and end != inspectorFocus:
            if end.bound.w <= canvas.canvasx(event.x) <= end.bound.e \
                    and end.bound.n <= canvas.canvasy(event.y) <= end.bound.s:
                inspectorFocus.pushesTo = end
                end.pullsFrom = inspectorFocus
                refreshInspector()
                drawNodeConnections()
                break


def drawNodeConnections():  # draws pushing connections only
    for b in objectsArr:
        if not isinstance(b, Placeables.LayerBlock) or b.pushesTo is None:  # looking for start of network
            continue
        for s in b.nodes:
            for e in b.pushesTo.nodes:
                canvas.create_line(s.x, s.y, e.x, e.y, fill='cyan')  # color based on inspObj.weights[s][e]


def refreshCanvas():
    #  move objects as opposed to redraw.
    pass
# ==========


root = tk.Tk()
root.title('Visual AI')
root.geometry(f"{Const.WIDTH}x{Const.HEIGHT}")
root.update_idletasks()  # strangely necessary to use winfo

toolbar = tk.Frame(root, bg=Const.COL_A)
toolbar.place(relwidth=1, relheight=0.1)

# panels
panelA = tk.PanedWindow(root, bd=1, relief='raised', bg='gray', sashwidth=2, sashrelief='raised')
panelA.place(relheight=0.9, relwidth=1, rely=0.1)
# inspector = tk.Frame(panelA, bg=Const.COL_A)
# panelA.add(inspector, width=root.winfo_width() / 3)
panelB = tk.PanedWindow(panelA, orient='vertical', bd=0, relief='sunken', bg='gray', sashwidth=2, sashrelief='raised')
panelA.add(panelB, width=root.winfo_width() * 2 / 3)
canvas = tk.Canvas(panelB, bg=Const.COL_B, highlightthickness=0)
panelB.add(canvas, height=Const.HEIGHT * 7 / 10)
shelf = tk.Frame(panelB, bg=Const.COL_A)
panelB.add(shelf)
panelC = tk.PanedWindow(panelA, orient='vertical', bd=0, relief='sunken', bg='gray', sashwidth=2, sashrelief='raised')
panelA.add(panelC)
hierarchy = tk.Frame(panelA, bg=Const.COL_A)
panelC.add(hierarchy, height=root.winfo_height() / 3)
inspector = tk.Frame(panelA, bg=Const.COL_A)
panelC.add(inspector)

# ---CANVAS----------------------------------------------------------
# pan and scroll
scrollbarX = tk.Scrollbar(canvas, orient='horizontal', command=canvas.xview)
scrollbarY = tk.Scrollbar(canvas, orient='vertical', command=canvas.yview)
# scrollbarX.pack(side="bottom", fill="x")
# scrollbarY.pack(side='right', fill='y')
canvas.configure(scrollregion=(0, 0, 2000, 1500), xscrollcommand=scrollbarX.set, yscrollcommand=scrollbarY.set)
canvas.yview_moveto(0.5)
canvas.xview_moveto(0.5)

canvas.bind('<ButtonPress-2>', pan_start)
canvas.bind('<B2-Motion>', pan_move)
# right click menu
m = tk.Menu(root, tearoff=0, bg=Const.COL_A, fg='white', activebackground=Const.COL_HI)
addmenu = tk.Menu(root, tearoff=0, bg=Const.COL_A, fg='white', activebackground=Const.COL_HI)
m.add_cascade(label='Add', menu=addmenu)
m.add_separator()
m.add_command(label="Cut")
m.add_command(label="Copy")
m.add_command(label="Paste")
m.add_command(label="Reload")

addmenu.add_command(label='Solo', command=addCircle)
addmenu.add_command(label='Layer', command=addLayerBlock)

canvas.bind("<Button-3>", do_popupMenu)
canvas.tag_bind('draggable', '<Button-1>', selectPlaceable)
canvas.tag_bind('draggable', '<B1-Motion>', dragPlaceable)
canvas.tag_bind('draggable', '<ButtonRelease-1>', forgetPlaceable)
canvas.tag_bind('inspectable', '<Button-1>', setInspectorFocus)
canvas.tag_bind('linkable', '<ButtonRelease-1>', setLinkEnd)

createGridLines(2000, 1500, 50)
# grid


# ---HIERARCHY-----------------------------------------------------
objListBox = tk.Listbox(hierarchy, bg=Const.COL_A, fg='white', relief='sunken', highlightthickness=0)
olb_scrollbar = tk.Scrollbar(objListBox, width=10, command=objListBox.yview)
# olb_scrollbar.pack(side='right', fill='y')
objListBox.configure(yscrollcommand=olb_scrollbar.set)
objListBox.place(anchor='n', y=30, relx=0.5, relwidth=0.75, relheight=0.8, )
tk.Label(hierarchy, text='Objects List', fg='white', bg=Const.COL_A).place(anchor='n', y=9, relx=0.25)
# ---INSPECTOR-------------------------------------------------------

# label
toolbar_label = tk.Label(toolbar, text="Toolbar", bg='red')
toolbar_label.pack()
inspector_label = tk.Label(inspector, text="Inspector", bg='yellow')
inspector_label.pack()
canvas_label = tk.Label(canvas, text="Canvas", bg='green')
canvas_label.pack()
shelf_label = tk.Label(shelf, text="Shelf", bg='orange')
shelf_label.pack()

root.mainloop()
