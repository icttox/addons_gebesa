odoo.define('hello_world.main', function (require) {
  "use strict";
  var rpc = require('web.rpc');
  var FormController = require('web.FormController');

  FormController.include({
  	_onButtonClicked: function (event) {
    	if(event.data.attrs.id === "validarlas"){
        this._rpc({
          model: 'res.company',
          method: 'validar_fiel',
          args: [{'id': this.getSelectedIds()}],
        }).then(function(result){
          if (result == true){
           $('#validarlas').children('i').attr('class','fa fa-fw o_button_icon fa-check-circle')
          }
        });
        return;
    	}
      else if(event.data.attrs.id === "descargamasiva"){
           $('.descarga-masiva').attr('style','')
           $('.descarga-data').attr('style','display: none')
           $('#descarg-return').attr('style','')
           $('#descargamasiva').attr('style','display: none')
           return;
      }
      else if(event.data.attrs.id === "descarg-return"){
           $('.descarga-masiva').attr('style','display: none')
           $('.descarga-data').attr('style','')
           $('#descarg-return').attr('style','display: none')
           $('#descargamasiva').attr('style','')
           return;
      }
      else if(event.data.attrs.id === "descarga-inicio"){
            this._rpc({
              model: 'res.company',
              method: 'descargamasiva',
              args: [{
                'id': this.getSelectedIds(),
                'start': $('#start').val(),
                'end': $('#final').val(),
                'tipo_solicitud': $('#tipo_solicitud option:selected').val(),
              }],
            }).then(function(result){
              var a = document.createElement("a"); //Create <a>
              a.href = "data:application/zip;base64," + result['paquete_b64']; //Image Base64 Goes here
              a.download = "Image.zip"; //File name Here
              a.click(); //Downloaded file

            });
            return;
      }
      this._super(event);
  	},
  });

});

function base64ToBuffer(str){
    str = window.atob(str); // creates a ASCII string
    var buffer = new ArrayBuffer(str.length),
        view = new Uint8Array(buffer);
    for(var i = 0; i < str.length; i++){
        view[i] = str.charCodeAt(i);
    }
    return buffer;
}
