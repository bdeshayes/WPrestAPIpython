<?php
/*
Plugin Name: REST-API
Plugin URI: 
Description: Adds the Press Releases custom post type.
Author: Bruno Deshayes
Version: 1.0
Author URI: 
*/

######################################
#                                    #
#  press_releases_init               #
#                                    #
######################################
// Creates Press Releases Custom Post Type
function press_releases_init() 
{
$args = array(
'label' => 'Press Releases',
'name' => 'press releases',
'singular_name' => 'press release',
'public' => true,
'has_archive'         => true, ###

'show_ui' => true,
'capability_type' => 'post',
'hierarchical' => false,
'taxonomies'          => array( 'category', 'tag' ),

/*  'rewrite' => array(
    'slug' => 'press_releases',
    'with_front'          => true,
    'pages'               => true,
    'feeds'               => true,
    ),*/
'query_var' => true,
'menu_icon' => 'dashicons-video-alt',

'show_in_rest'       => true,
'rest_base'          => 'press_releases',
'rest_controller_class' => 'WP_REST_Posts_Controller',


'supports' => array(
    'title',
    'editor',
    'excerpt',
    'trackbacks',
    'custom-fields',
    'comments',
    'revisions',
    'thumbnail',
    'author',
    'page-attributes',)
);
register_post_type( 'press_releases', $args );
}

add_action( 'init', 'press_releases_init' );

// The object type. For custom post types, this is 'post';
// for custom comment types, this is 'comment'. For user meta,
// this is 'user'.
$object_type = 'post';
$args1 = array
( // Validate and sanitize the meta value.
// Note: currently (4.7) one of 'string', 'boolean', 'integer',
// 'number' must be used as 'type'. The default is 'string'.
'type'         => 'string',
// Shown in the schema for the meta key.
'description'  => 'A meta key associated with a string meta value.',
// Return a single value of the type.
'single'       => true,
// Show in the WP REST API response. Default: false.
'show_in_rest' => true,
);
register_meta( $object_type, 'topic', $args1 );
register_meta( $object_type, 'link', $args1 );
register_meta( $object_type, 'desk', $args1 );

add_action('admin_menu', 'pr_button_menu');

######################################
#                                    #
#  press_releases_init               #
#                                    #
######################################
function pr_button_menu(){
  add_menu_page('PR Generator Page', 'PR Generator', 'manage_options', 'pr-button-slug', 'pr_button_admin_page');

}

######################################
#                                    #
#  press_releases_init               #
#                                    #
######################################
function pr_button_admin_page() {

  // This function creates the output for the admin page.
  // It also checks the value of the $_POST variable to see whether
  // there has been a form submission. 

  // The check_admin_referer is a WordPress function that does some security
  // checking and is recommended good practice.

  // General check for user permissions.
  if (!current_user_can('manage_options'))  {
    wp_die( __('You do not have sufficient pilchards to access this page.')    );
  }

  // Start building the page

  echo '<div class="wrap">';

  echo '<h2>Press Releases Generator</h2>';

  // Check whether the button has been pressed AND also check the nonce
  if (isset($_POST['pr_button']) && check_admin_referer('pr_button_clicked')) {
    // the button has been pressed AND we've passed the security check
    pr_button_action();
  }

  echo '<form action="options-general.php?page=pr-button-slug" method="post">';

  echo "WARNING - all current press releases will be removed!<br /><br />";
  // this is a WordPress security feature - see: https://codex.wordpress.org/WordPress_Nonces
  wp_nonce_field('pr_button_clicked');
  echo '<input type="hidden" value="true" name="pr_button" />';
  submit_button('Generate sample data');
  echo '</form>';

  echo '</div>';

}
function convert_to_normal_text($text) 
{
return $text;
/*$normal_characters = "a-zA-Z0-9\s`~!@#$%^&*()_+-={}|:;<>?,.\/\"\'\\\[\]";
$normal_text = preg_replace("/[^$normal_characters]/", '', $text);

return $normal_text;*/
}
######################################
#                                    #
#  press_releases_init               #
#                                    #
######################################
function pr_button_action()
{
  echo '<div id="message" class="updated fade"><p>'
    .'All done - go to the menu Press Releases to see the result' . '</p></div>';

  $path = WP_TEMP_DIR . '/pr-button-log.txt';

  $handle = fopen($path,"w");

  if ($handle == false) {
    echo '<p>Could not write the log file to the temporary directory: ' . $path . '</p>';
  }
  else {
    echo '<p>Log of button click written to: ' . $path . '</p>';

    fwrite ($handle , "Call Function button clicked on: " . date("D j M Y H:i:s", time())."\n"); 

/*$args = array(
	'posts_per_page'   => 5,
	'offset'           => 0,
	'cat'         => '',
	'category_name'    => '',
	'orderby'          => 'date',
	'order'            => 'DESC',
	'include'          => '',
	'exclude'          => '',
	'meta_key'         => '',
	'meta_value'       => '',
	'post_type'        => 'post',
	'post_mime_type'   => '',
	'post_parent'      => '',
	'author'	   => '',
	'author_name'	   => '',
	'post_status'      => 'publish',
	'suppress_filters' => true,
	'fields'           => '',
);*/
$posts_array = get_posts( array('post_type' => 'press_releases', 'posts_per_page'   => -1) );

foreach ($posts_array as $post)
    {
    fwrite ($handle , "deleting id {$post->ID}\n");
    wp_delete_post($post->ID, true); 
    }
    
$desks = array(
"New York",
"San Francisco",
"Cincinnati",
"Las Vegas",
"Los Angeles",
"Seattle",
"Minneapolis",
"Houston",
"Miami",
"London",
"Paris",
"Berlin",
"Madrid",
"Rome",
"Dublin",
"Zurich",
"Copenhagen",
"Rotterdam",
"Sydney",
"Melbourne",
"Brisbane",
);

$feed_url = "https://www.prurgent.com/news/rss.php";
$x = new SimpleXmlElement(file_get_contents($feed_url));
 
foreach($x->channel->item as $entry) 
    {
    $dkey = array_rand ($desks);
    $mydesk = $desks[$dkey];

    $postarr = array (
    #'ID' (int) The post ID. If equal to something other than 0, the post with that ID will be updated. Default 0.
    'post_author' => 1, #(int) The ID of the user who added the post. Default is the current user ID.
    #'post_date' (string) The date of the post. Default is the current time.
    #'post_date_gmt' (string) The date of the post in the GMT timezone. Default is the value of $post_date.
    'post_content' => convert_to_normal_text((string)$entry->description), #(mixed) The post content. Default empty.
    #'post_content_filtered' (string) The filtered post content. Default empty.
    'post_title' => convert_to_normal_text((string)$entry->title), #(string) The post title. Default empty.
    #'post_excerpt' (string) The post excerpt. Default empty.
    'post_status' => 'publish', # (string) The post status. Default 'draft'.
    'post_type' => 'press_releases', #(string) The post type. Default 'post'.
    'comment_status' => 'closed', #(string) Whether the post can accept comments. Accepts 'open' or 'closed'. Default is the value of 'default_comment_status' option.
    #'ping_status' (string) Whether the post can accept pings. Accepts 'open' or 'closed'. Default is the value of 'default_ping_status' option.
    #'post_password' (string) The password to access the post. Default empty.
    #'post_name' (string) The post name. Default is the sanitized post title when creating a new post.
    #'to_ping' (string) Space or carriage return-separated list of URLs to ping. Default empty. 'pinged' (string) Space or carriage return-separated list of URLs that have been pinged. Default empty.
    #'post_modified' (string) The date when the post was last modified. Default is the current time.
    #'post_modified_gmt' (string) The date when the post was last modified in the GMT timezone. Default is the current time.
    #'post_parent' (int) Set this for the post it belongs to, if any. Default 0.
    #'menu_order' (int) The order the post should be displayed in. Default 0.
    #'post_mime_type' (string) The mime type of the post. Default empty.
    #'guid' (string) Global Unique ID for referencing the post. Default empty.
    #'post_category' => array ((string)$entry->category), #(array) Array of category names, slugs, or IDs. Defaults to value of the 'default_category' option.
    #'tags_input' => array ((string)$entry->category), # (array) Array of tag names, slugs, or IDs. Default empty.
    #'tax_input' (array) Array of taxonomy terms keyed by their taxonomy name. Default empty.
    'meta_input' => array ('topic' => (string)$entry->category, 
                            'desk' => $mydesk, 
                            'link' =>  (string)$entry->link) # (array) Array of post meta values keyed by their post meta key. Default empty.
    );
    
    $retval = wp_insert_post($postarr);
    fwrite ($handle , "$i- wp_insert_post() returns $retval\n");
    }
    
    fclose ($handle);
  }

}  
?>
