odoo.define('website_production_load.WebsiteProductionLoad', function (require) {

    var rpc = require('web.rpc');

    function Comparator(a, b) {
        if (a[1] < b[1]) return -1;
        if (a[1] > b[1]) return 1;
        return 0;
    }

    $(document).on("change", "#prod_load_employee_number", function (){
        const $input = document.getElementById("prod_load_employee_number");

        document.getElementById('div_prod_load_workcenter_id').style.display = 'none';
        document.getElementById('div_prod_load_product_id').style.display = 'none';
        document.getElementById('div_prod_load_qty').style.display = 'none';
        document.getElementById('div_prod_load_operation_id').style.display = 'none';
        document.getElementById('div_prod_load_comments').style.display = 'none';
        document.getElementById('div_prod_load_submit').style.display = 'none';

        if($input.value !== ""){
            document.getElementById('div_prod_load_workcenter_id').style.display = 'block';
            return;
        }

        document.getElementById('prod_load_workcenter_id').value = '';
        document.getElementById('prod_load_qty').value = '';
        document.getElementById('prod_load_operation_id').value = '';
        document.getElementById('prod_load_comments').value = '';

    });


    $(document).on("change", "#prod_load_workcenter_id", function (){
        const $input = document.getElementById("prod_load_workcenter_id");
        const option = document.createElement('option');

        document.getElementById('div_prod_load_product_id').style.display = 'none';
        document.getElementById('div_prod_load_qty').style.display = 'none';
        document.getElementById('div_prod_load_operation_id').style.display = 'none';
        document.getElementById('div_prod_load_comments').style.display = 'none';
        document.getElementById('div_prod_load_submit').style.display = 'none';

        const indice = $input.selectedIndex;
        if(indice === 0){
            return; // Esto es cuando no hay elementos
        }
        const opcionSeleccionada = $input.options[indice];


        const $ul_product = document.getElementById("ul_prod_load_product");
        

        const listItems = document.querySelectorAll('#ul_prod_load_product li');
        listItems.forEach(listItem => {
            listItem.parentNode.removeChild(listItem);
        });

        rpc.query({
            model: 'product.product',
            method: 'search_read',
            args: [[['workcenter_id', '=', parseInt(opcionSeleccionada.value)]], ['id','default_code', 'image']],
        }).then(function (countigs) {
            if (countigs.length > 0) {
                _.each(countigs, function(select) {
                    const li_check = document.createElement('li');
                    li_check.classList.add('list-inline-item', 'col-md-3', 'bg-white', 'mx-auto', 'text-center', 'pagination-centered');
                    li_check.setAttribute('id', 'li_' + select.default_code);

                    var checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = select.default_code;
                    checkbox.name = 'product_' + select.id.toString()
                    checkbox.classList.add('prod_load_checkbox');
                    checkbox.onclick = function LiCheckProductOnlyOne(checkbox) {
                        var checkboxes = document.getElementsByClassName('prod_load_checkbox')
                        Array.from(checkboxes).forEach(function(element, index, array) {
                            if (element.id !== checkbox.currentTarget.id)
                            {
                                element.checked = false
                            } else if (element.checked) {
                                document.getElementById('div_prod_load_qty').style.display = 'block';
                            } else {
                                document.getElementById('div_prod_load_qty').style.display = 'none';
                                document.getElementById('div_prod_load_operation_id').style.display = 'none';
                                document.getElementById('div_prod_load_comments').style.display = 'none';
                                document.getElementById('div_prod_load_submit').style.display = 'none';
                                document.getElementById("prod_load_qty").value = "";
                                document.getElementById('prod_load_operation_id').value = '';
                                document.getElementById('prod_load_comments').value = '';
                            }
                        });
                    };

                    var label = document.createElement('label');
                    label.htmlFor = checkbox.id;
                    var labelTextNode = document.createTextNode(select.default_code);
                    label.appendChild(labelTextNode);

                    var br = document.createElement("br");
                    label.appendChild(br);

                    var img = new Image();
                    imgStr64 = select.image;
                    img.src = "data:image/jpg;base64," + imgStr64;
                    label.appendChild(img);

                    li_check.appendChild(checkbox);
                    li_check.appendChild(label);

                    $ul_product.appendChild(li_check);

                });
                document.getElementById('div_prod_load_product_id').style.display = 'block';
                document.getElementById('prod_load_qty').value = '';
                document.getElementById('prod_load_operation_id').value = '';
                document.getElementById('prod_load_comments').value = '';
            }
        });
    });


    $(document).on("change", "#prod_load_qty", function (){
        const $input = document.getElementById("prod_load_qty");

        document.getElementById('div_prod_load_operation_id').style.display = 'none';
        document.getElementById('div_prod_load_comments').style.display = 'none';
        document.getElementById('div_prod_load_submit').style.display = 'none';

        if($input.value !== "" && $input.value !== "0"){
            document.getElementById('div_prod_load_operation_id').style.display = 'block';
            return;
        }

        document.getElementById('prod_load_operation_id').value = '';
        document.getElementById('prod_load_comments').value = '';
    });

    $(document).on("change", "#prod_load_operation_id", function (){
        const $input = document.getElementById("prod_load_operation_id");

        document.getElementById('div_prod_load_comments').style.display = 'none';
        document.getElementById('div_prod_load_submit').style.display = 'none';

        const indice = $input.selectedIndex;
        if(indice === 0){
            return; // Esto es cuando no hay elementos
        }

        document.getElementById('div_prod_load_comments').style.display = 'block';
        document.getElementById('div_prod_load_submit').style.display = 'block';
    });

});