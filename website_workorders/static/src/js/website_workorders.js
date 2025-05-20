odoo.define('website_workorders.WebsiteWorkOrders', function (require) {

    var rpc = require('web.rpc');

	$(document).on("change", "#web_wor_ord_workcenter_id", function (){
        const $input = document.getElementById("web_wor_ord_workcenter_id");
        const $select2 = document.getElementById("web_wor_ord_product_id");

        for (let i = $select2.options.length; i > 0; i--) {
            $select2.remove(i);
        }

        const indice = $input.selectedIndex;
        if(indice === 0){
            return; // Esto es cuando no hay elementos
        }
        const opcionSeleccionada = $input.options[indice];

        rpc.query({
            model: 'mrp.routing.workcenter',
            method: 'get_products_production_load',
            args: [[], parseInt(opcionSeleccionada.value)],
        }).then(function (products) {
            if (products.length > 0) {
                _.each(products, function(select) {
                    const option = document.createElement('option');
                    option.value = select.id;
                    option.text = select.name;
                    $select2.appendChild(option);

                });
            }
        });
    });
});