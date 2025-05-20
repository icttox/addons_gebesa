odoo.define('website_quality.Quality', function (require) {

    var rpc = require('web.rpc');

    function Comparator(a, b) {
        if (a[1] < b[1]) return -1;
        if (a[1] > b[1]) return 1;
        return 0;
    }

    $(document).on("change", "#order_id", function (){
        const $input = document.getElementById("order_id");
        const $select2 = document.getElementById("product_id");
        const option = document.createElement('option');

        for (let i = $select2.options.length; i > 0; i--) {
            $select2.remove(i);
        }

        // const indice = $select.selectedIndex;
        // if(indice === -1) return; // Esto es cuando no hay elementos
        //     const opcionSeleccionada = $select.options[indice];

        rpc.query({
            model: 'mrp.production',
            method: 'get_product_from_sale',
            args: [[],$input.value]
        }).then(function (products) {
            var select_product = []
            select_product = products.sort(Comparator);
            _.each(select_product, function(select) {
                const option = document.createElement('option');
                option.value = select[0];
                option.text = select[1];
                $select2.appendChild(option);
            });
        });
    });

    $(document).on("change", "#workcenter_id", function (){
        const $select = document.getElementById("workcenter_id");
        const $select2 = document.getElementById("flaw_id");
        const option = document.createElement('option');

        for (let i = $select2.options.length; i > 0; i--) {
            $select2.remove(i);
        }

        const indice = $select.selectedIndex;
        if(indice === -1) return; // Esto es cuando no hay elementos
            const opcionSeleccionada = $select.options[indice];

        rpc.query({
            model: 'quality.alert.flaw',
            method: 'search_read',
            args: [[['workcenter_ids', 'in', [parseInt(opcionSeleccionada.value)]]]]
        }).then(function (flaws) {
            _.each(flaws, function(select) {
                const option = document.createElement('option');
                option.value = select.id;
                option.text = select.display_name;
                $select2.appendChild(option);
            });
        });
    });

});