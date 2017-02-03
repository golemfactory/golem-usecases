from xml.dom.minidom import parseString


def regenerate_indigo_file(scene_file_src, xres, yres):
    scene_file_dom = parseString(scene_file_src)
    scene_dom = scene_file_dom.getElementsByTagName("scene")[0]
    renderer_settings_dom = scene_dom.getElementsByTagName("renderer_settings")[0]
    width_dom = renderer_settings_dom.getElementsByTagName("width")[0]
    height_dom = renderer_settings_dom.getElementsByTagName("height")[0]
    width_dom.childNodes[0].data = u"{}".format(xres)
    height_dom.childNodes[0].data = u"{}".format(yres)
    return scene_file_dom.toxml()



