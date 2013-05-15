function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function updateCategoryList(after_success_func){
	$.post("/category/list",
			{_xsrf:getCookie("_xsrf")},
			function(data, textStatus, jqXHR){
				categorys = JSON.parse(data)
				$("#categorylist").children().remove()
				clist = $("#categorylist")
				newelement = "";
				for(i = 0; i<categorys.length; i++){
					c= categorys[i];
					if(c['parent'] == 0){
						newelement += "<li><label class='checkbox'><input value='"+c['id']+"' type='checkbox' name='post_category[]' id='post_category_"+c['id']+"'/>"+c['name']+"</label>";
						
						newelement += "<ul class='nav nav-list'>";
						for(j = 0; j<categorys.length; j++){
							sc = categorys[j]
							if(sc['parent'] == c['id'])
							{
								newelement += "<li><label class='checkbox'><input value='"+sc['id']+"' type='checkbox' name='post_category[]' id='post_category_"+sc['id']+"'/>"+sc['name']+"</label></li>";
							}
						}
						newelement += "</ul></li>";
					}
				}
				clist.append(newelement);
				if(after_success_func)
				    after_success_func();
			}
	);
}
$(function(){
	$("#category_quickadd").click(function() {
		var name = $("#new_category").val();
		if(name == ""){
			alert("please input the category name!");
			return;
		}
		_xsrf__ = getCookie("_xsrf");
		var selectedItems = new Array();
		$("input[name='post_category[]']:checked").each(function() {selectedItems.push($(this).val());});
		if (selectedItems .length == 0)
		    selectedItems.push(0);
		$.post("/admin/category/quickadd",
			{_xsrf:_xsrf__,
			 name:$("#new_category").val(),
			 parent:selectedItems.join(",")},
			function(data, textStatus, jqXHR){
				updateCategoryList(function()
				{
					//new_category_name = $("#new_category").val();
					$("#new_category").val('')
				});
			});
	});
})


