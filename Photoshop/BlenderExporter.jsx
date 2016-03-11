#target Photoshop

var doc = app.activeDocument;
var layers = doc.layers;
var coords = [];
var exporter_version = "v1.0 Beta"

//Save Options for PNGs
var options = new ExportOptionsSaveForWeb();
options.format = SaveDocumentType.PNG;
options.PNG8 = false;
options.transparency = true;
options.optimized = true;

function deselect_all_layers() {   
    var desc01 = new ActionDescriptor();   
        var ref01 = new ActionReference();   
        ref01.putEnumerated( charIDToTypeID('Lyr '), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );   
    desc01.putReference( charIDToTypeID('null'), ref01 );   
    executeAction( stringIDToTypeID('selectNoLayers'), desc01, DialogModes.NO );
}

function save_coords(center_sprites,export_path, export_name){
    var json_file = new File(export_path+"/"+export_name+".json");
    json_file.open('w');
    json_file.writeln("{");
    json_file.writeln('"object_name":'+'"'+export_name+'",');
    if(center_sprites == true){
        json_file.writeln('"offset":'+'['+doc.width.as("px")*-.5+',0,'+doc.height.as("px")*.5+'],');
    }else{
        json_file.writeln('"offset":'+'[0,0,0],');
    }    
    json_file.writeln('"sprites":[');
    for(i = 0; i < coords.length; i++){
        //json_file.writeln(key+" = ("+coords[key][0]+","+coords[key][1]+")");
        var line = '    {"'+coords[i][0]+'":{"name":"'+coords[i][0]+'","pos":['+coords[i][1][0]+','+coords[i][1][1]+','+coords[i][1][2]+'],"tilesize":['+coords[i][2][0]+','+coords[i][2][1]+']}}';
        if(i < coords.length-1){
            line += ","
        }    
        json_file.writeln(line);
    }
    json_file.writeln('    ]');
    json_file.writeln("}");
    json_file.close();
}

function extend_document_size(size_x, size_y){
// =======================================================
    var idCnvS = charIDToTypeID( "CnvS" );
        var desc8 = new ActionDescriptor();
        var idWdth = charIDToTypeID( "Wdth" );
        var idPxl = charIDToTypeID( "#Pxl" );
        desc8.putUnitDouble( idWdth, idPxl, size_x );
        var idHght = charIDToTypeID( "Hght" );
        var idPxl = charIDToTypeID( "#Pxl" );
        desc8.putUnitDouble( idHght, idPxl, size_y );
        var idHrzn = charIDToTypeID( "Hrzn" );
        var idHrzL = charIDToTypeID( "HrzL" );
        var idLeft = charIDToTypeID( "Left" );
        desc8.putEnumerated( idHrzn, idHrzL, idLeft );
        var idVrtc = charIDToTypeID( "Vrtc" );
        var idVrtL = charIDToTypeID( "VrtL" );
        var idTop = charIDToTypeID( "Top " );
        desc8.putEnumerated( idVrtc, idVrtL, idTop );
    executeAction( idCnvS, desc8, DialogModes.NO );
}    

function duplicate_into_new_doc(){
    // =======================================================
    var idMk = charIDToTypeID( "Mk  " );
        var desc231 = new ActionDescriptor();
        var idnull = charIDToTypeID( "null" );
            var ref114 = new ActionReference();
            var idDcmn = charIDToTypeID( "Dcmn" );
            ref114.putClass( idDcmn );
        desc231.putReference( idnull, ref114 );
        var idNm = charIDToTypeID( "Nm  " );
        desc231.putString( idNm, """dupli_layers_doc""" );
        var idUsng = charIDToTypeID( "Usng" );
            var ref115 = new ActionReference();
            var idLyr = charIDToTypeID( "Lyr " );
            var idOrdn = charIDToTypeID( "Ordn" );
            var idTrgt = charIDToTypeID( "Trgt" );
            ref115.putEnumerated( idLyr, idOrdn, idTrgt );
        desc231.putReference( idUsng, ref115 );
        var idVrsn = charIDToTypeID( "Vrsn" );
        desc231.putInteger( idVrsn, 5 );
    executeAction( idMk, desc231, DialogModes.NO );
}    

function export_sprites(export_path , export_name , crop_to_dialog_bounds , center_sprites){
    // check if folder exists. if not, create one
    var export_folder = new Folder(export_path);
    if(!export_folder.exists) export_folder.create();
    
    var tmp_layers = doc.layers;
    
    duplicate_into_new_doc();
    var dupli_doc = app.activeDocument;
    var selected_layer = dupli_doc.layers;
    
    /// deselect all layers and select first with this hack of adding a new layer and then deleting it again
    var testlayer = dupli_doc.artLayers.add();
    testlayer.remove();
    ///
    
    for(i = 0; i < selected_layer.length; i++){ 
        // deselect layers
        var layer = selected_layer[i];
        
        dupli_doc.activeLayer = layer;
        
        var bounds_width = layer.bounds[2] - layer.bounds[0];
        var bounds_height = layer.bounds[3] - layer.bounds[1];
        var layer_pos = Array(layer.bounds[0].as("px"),i,layer.bounds[1].as("px"));
        var tmp_doc = app.activeDocument;
        var layer_name = String(layer.name).split(' ').join('_');
        var tile_size = [1,1]        
        var tmp_doc = app.documents.add( dupli_doc.width , dupli_doc.height , dupli_doc.resolution , layer_name , NewDocumentMode.RGB , DocumentFill.TRANSPARENT );
    
        app.activeDocument = dupli_doc;
        //alert(layer.name);
        layer.duplicate(tmp_doc , ElementPlacement.INSIDE);
        app.activeDocument = tmp_doc;
        var crop_bounds = layer.bounds;
        
        if(crop_to_dialog_bounds == true){
            if(crop_bounds[0].value < 0){ crop_bounds[0] = 0 };
            if(crop_bounds[1].value < 0){ crop_bounds[1] = 0 };
            if(crop_bounds[2].value > doc.width.value){ crop_bounds[2] = doc.width.value };
            if(crop_bounds[3].value > doc.height.value){ crop_bounds[3] = doc.height.value };
        }
        
        tmp_doc.crop(crop_bounds);

        if (layer_name.indexOf("--sprites") != -1){
            var keyword_pos = layer_name.indexOf("--sprites") ;
            var sprites = tmp_doc.layers[0].layers;
            var sprite_count = sprites.length;
            if (column_str_index = layer_name.indexOf("c=") != -1){
                var column_str_index = layer_name.indexOf("c=")+2;
                var columns = parseInt(layer_name.substring(column_str_index,layer_name.length));
            }else{
                var columns = parseInt(Math.sqrt(sprite_count)+0.5);
            }
            tile_size = [columns,parseInt(sprite_count/columns + 0.5)];
            $.writeln(tile_size);
            if (layer_name[keyword_pos - 1] == "_"){
                layer_name = layer_name.substring(0,keyword_pos - 1);
            }else{
                layer_name = layer_name.substring(0,keyword_pos);
            }
            var k = 0;
            for(j=0;j<sprites.length;j++){
                if(j>0 && j%columns == 0){
                    k = k+1;
                }
                sprites[j].translate(tmp_doc.width * (j%columns), tmp_doc.height * k);
            }

            extend_document_size(tmp_doc.width * columns, tmp_doc.height * (k+1));

        }
        // do save stuff
        tmp_doc.exportDocument(File(export_path+"/"+layer_name+".png"),ExportType.SAVEFORWEB,options );
        
        // store coords
        coords.push([layer_name+".png",layer_pos,tile_size]);
        
        // close tmp doc again
        tmp_doc.close(SaveOptions.DONOTSAVECHANGES);
    }
    dupli_doc.close(SaveOptions.DONOTSAVECHANGES);
    save_coords(center_sprites,export_path, export_name);
} 

function export_button(){
    try{
            win.export_name.text = String(win.export_name.text).split(' ').join('_');
            app.activeDocument.info.caption = win.export_path.text;
            app.activeDocument.info.captionWriter = win.export_name.text;
            //export_sprites(win.export_path.text, win.export_name.text, win.limit_layer.value, win.center_sprites.value);
            app.activeDocument.suspendHistory("Export selected Sprites","export_sprites(win.export_path.text, win.export_name.text, win.limit_layer.value, win.center_sprites.value)");
            win.close();
    }catch (e){
        win.close();
        alert ("No selected layer to export.", "Warning");
        return;
    }
}    

function path_button(){
    var folder_path = Folder.selectDialog ("Select Place to save");
    if (folder_path != null){
        win.export_path.text = folder_path  ;
        app.activeDocument.info.caption = folder_path;
    }
}    

var win = new Window("dialog", 'Json Exporter '+exporter_version, [0,0,445,117], );
with(win){
	win.export_path = add( "edittext", [85,15,365,35], 'export_path' );
	win.sText = add( "statictext", [5,20,75,40], 'Export Path:' );
	win.limit_layer = add( "checkbox", [5,70,180,90], 'Limit layers by Document' );
	win.center_sprites = add( "checkbox", [5,90,180,110], 'Center Sprites in Blender' );
	win.export_button = add( "button", [340,90,440,112], 'Export Layers' );
	win.export_name = add( "edittext", [85,40,440,60], 'export_name' );
	win.sText2 = add( "statictext", [5,45,85,65], 'Export Name:' );
	win.button_path = add( "button", [370,13,440,35], 'select' );
	}
win.export_path.text = app.activeDocument.info.caption;
win.export_name.text = app.activeDocument.info.captionWriter;
win.export_button.onClick = export_button;
win.button_path.onClick = path_button;
win.center_sprites.value = true;
win.limit_layer.value = true;
win.center();
win.show();
