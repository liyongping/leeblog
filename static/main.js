function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function ReplyComment(commentid, id){
	// move addcomment form
	$('#addcomment').insertAfter('#'+commentid);
	$('#cancel-reply').show();
	$('#comment_parent_id').val(id);
	return false;
}

function ResetReply(){
	$('#addcomment').appendTo('#main');
	$('#cancel-reply').hide();
	$('#comment_parent_id').val(0);
}

function SetComment(commentid, data, parentdata){
	content = $('#'+commentid)
	comment_meta = content.children('.comment-meta');
	// 设置作者信息
	comment_meta.children('.comment-author').children('.author-link')
		.attr({"href":data['author_url']}) // 设置作者URL
		.text(data['author'])// 设置作者名字
	// 设置发布时间
	comment_meta.children('.comment-time').children('.published')
		.text(data['date'])
	comment_meta.children('.comment-rely').children('.comment-reply-link')
		.attr({"href":data['author_url'],
				"onclick":"return ReplyComment('"+commentid+"',"+data['id']+")"}) // 设置回复URL
	parentTip = "";
	if(parentdata!=null && parentdata!="")
		parentTip = "@"+parentdata['author']+": "
	// 设置内容
	content.children('.text').text(parentTip + data['content']);
}

function AddComment(commentid, data, parentdata){
	comment = $('#comment-template').clone().removeAttr('style').removeAttr('id');
	// 设置ID
	comment.children('.comment').attr({"id":commentid});
	comment.appendTo('#comment-list');
	SetComment(commentid, data, parentdata);
}

function AddSubComment(commentid, karmaid, data, parentdata){
	comment = $('#comment-template').clone().removeAttr('style').removeAttr('id');
	// 设置ID
	comment.children('.comment').attr({"id":commentid});
	vcc = comment.appendTo('#'+karmaid+' + ul.children');
	vc = $('#'+karmaid+' + ul.children');
	vc1 = $('#comment-12 + ul.children')
	SetComment(commentid, data, parentdata);
}

function FindParentData(parentid, data){
	for(var i = 0; i<data.length; i++){
		if(data[i].id == parentid)
			return data[i];
		}
	return "";
}
	
function UpdateCommentList(){
	comment_post_id = $("#comment_post_id").val();
	$('#comment_parent_id').val(0);
	if(comment_post_id != undefined){
		$.post("/comment/list",
				{_xsrf:getCookie("_xsrf"),
				post_id:$("#comment_post_id").val()},
				function(data, textStatus, jqXHR){
					if(data.length == 0)
						return false;
					comments = JSON.parse(data);
					$("#comment-list").children().remove();
					for(var i = 0; i<comments.length; i++){
						c= comments[i];
						if(c['parent'] == 0){
							AddComment('comment-'+c['id'], c, FindParentData(c['parent'],comments));
							for(var j = 0; j<comments.length; j++){
								sc = comments[j]
								if(sc['karma'] == c['id'] && sc['parent'] != 0){
									AddSubComment('comment-'+sc['id'], 'comment-'+c['id'], sc, FindParentData(sc['parent'],comments));
								}
							}
						}
					}
					ResetReply();
				}
		);
	}
}

// post-submit callback 
function showResponse(responseText)  { 
    if(responseText != ""){
    	comment = JSON.parse(responseText);
    	if(comment.length != 2)
    		return;
    	ResetReply();
    	// comment[1] is current comment data. comment[0] is parent commnet data.
    	if (comment[1]['parent'] == 0) {
    		AddComment('comment-'+comment[1]['id'], comment[1], comment[0]);
    	}else{
    		AddSubComment('comment-'+comment[1]['id'], 'comment-'+comment[1]['karma'], comment[1], comment[0]);
    	}
    	newcount = parseInt($('#post-comment-count').text())+1;
    	$('#post-comment-count').text(newcount.toString())
    	
    }
}

$(function () {
	var options = { 
        //target:        '#output2',   // target element(s) to be updated with server response 
	    //beforeSubmit:  showRequest,  // pre-submit callback 
	    success:       showResponse,  // post-submit callback 
	    // other available options: 
	    //url:       url         // override for form's 'action' attribute 
	    //type:      type        // 'get' or 'post', override for form's 'method' attribute 
	    //dataType:  null        // 'xml', 'script', or 'json' (expected server response type) 
	    clearForm: true        // clear all form fields after successful submit 
	    //resetForm: true        // reset the form after successful submit 
	 
	        // $.ajax options can be used here too, for example: 
	    //timeout:   3000 
	};
	var rules = {
		rules: {
			author: {
				minlength: 2,
				required: true
			},
			email: {
				required: true,
				email: true
			},
			url: {
				url:true
			},
			comment: {
				minlength: 2,
				maxlength:500,
				required: true
			}
		},  
		submitHandler: function(form)
		   {
				$(form).ajaxSubmit(options);    
		   }
	};
	UpdateCommentList();
	$('#commentform').validate(rules);
	
});
