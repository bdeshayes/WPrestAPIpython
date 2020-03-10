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
'has_archive'         => true, 

'show_ui' => true,
'capability_type' => 'post',
'hierarchical' => false,
'taxonomies'          => array( 'category', 'tag' ),

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
function pr_button_admin_page() 
{
// This function creates the output for the admin page.
// It also checks the value of the $_POST variable to see whether
// there has been a form submission. 

// The check_admin_referer is a WordPress function that does some security
// checking and is recommended good practice.

// General check for user permissions.
if (!current_user_can('manage_options')) 
	wp_die( __('You do not have sufficient pilchards to access this page.')    );


// Start building the page

echo '<div class="wrap">';
echo '<h2>Press Releases Generator</h2>';
echo '<form action="options-general.php?page=pr-button-slug" method="post">';

// Check whether the button has been pressed AND also check the nonce
if (isset($_POST['pr_button']) && check_admin_referer('pr_button_clicked')) 
	{
	// the button has been pressed AND we've passed the security check
	pr_button_action();
	}
else
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
//return $text;
$normal_characters = "a-zA-Z0-9\s`~!@#$%^&*()_+-={}|:;<>?,.\/\"\'\\\[\]";
$normal_text = preg_replace("/[^$normal_characters]/", '', $text);

return $normal_text;
}

######################################
#                                    #
#  press_releases_init               #
#                                    #
######################################
function pr_button_action()
{
global $PRcount;
echo '<div id="message" class="updated fade"><p>' .
'All doen.<br />Go to the menu Press Releases to see the result' . '</p></div>';

$path = WP_TEMP_DIR . '/pr-button-log.txt';

$handle = fopen($path,"w");

if ($handle == false) 
	{
	echo '<p>Could not write the log file to the temporary directory: ' . $path . '</p>';
	}
 else 
	{
	fwrite ($handle , "Call Function button clicked on: " . date("D j M Y H:i:s", time())."\n"); 

	$posts_array = get_posts( array('post_type' => 'press_releases', 'posts_per_page'   => 200) );

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

	$x = new SimpleXmlElement("https://www.prurgent.com/news/rss.php", null, true);

	$i=0; 
	foreach($x->channel->item as $entry) 
		{
		$dkey = array_rand ($desks);
		$mydesk = $desks[$dkey];

		$postarr = array (
		'post_author' => 1, #(int) The ID of the user who added the post. Default is the current user ID.
		'post_content' => convert_to_normal_text((string)$entry->description), #(mixed) The post content. Default empty.
		'post_title' => convert_to_normal_text((string)$entry->title), #(string) The post title. Default empty.
		'post_status' => 'publish', # (string) The post status. Default 'draft'.   
		'post_type' => 'press_releases', #(string) The post type. Default 'post'.
		'comment_status' => 'closed', 
		'meta_input' => array ('topic' => (string)$entry->category, 
								'desk' => $mydesk, 
								'link' =>  (string)$entry->link) # (array) Array of post meta values keyed by their post meta key. Default empty.
		);

		$retval = wp_insert_post($postarr);
		fwrite ($handle , "$i- wp_insert_post() returns $retval\n");
		$i++;
		}

	fclose ($handle);
	echo "$i press releases loaded\n";
	}

}  
?>
