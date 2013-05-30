/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	config.language = 'zh-cn';
	config.filebrowserBrowseUrl = '/filemanager';
};

CKEDITOR.inline('inline_edit', {
    extraPlugins: 'fastimage'
});

CKEditor.replace('textareaId', {
        "extraPlugins": "imagebrowser",
        "imageBrowser_listUrl": "/path/to/images_list.json"
});