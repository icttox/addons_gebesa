odoo.define('website_maintenance_hr.Maintenance', function (require) {

    var rpc = require('web.rpc');

    function Comparator(a, b) {
        if (a[1] < b[1]) return -1;
        if (a[1] > b[1]) return 1;
        return 0;
    }

    $(document).on("change", "#ubication", function (){
        const $select = document.getElementById("ubication");
        const $select2 = document.getElementById("equipment");
        const option = document.createElement('option');

        for (let i = $select2.options.length; i > 0; i--) {
            $select2.remove(i);
        }

        const indice = $select.selectedIndex;
        if(indice === -1) return; // Esto es cuando no hay elementos
           const opcionSeleccionada = $select.options[indice];

        rpc.query({
            model: 'maintenance.equipment',
            method: 'get_equipment_from_location',
            args: [[], parseInt(opcionSeleccionada.value)]
        }).then(function (equipments) {
            _.each(equipments, function(select) {
                const option = document.createElement('option');
                option.value = select.id;
                option.text = select.name;
                $select2.appendChild(option);
            });
        });
    });

});