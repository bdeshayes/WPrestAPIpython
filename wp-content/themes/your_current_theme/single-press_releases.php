<?php
/**
 * The template for displaying all single posts
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/#single-post
 *
 * @package WordPress
 * @subpackage Twenty_Nineteen
 * @since 1.0.0
 */

get_header();
?>

	<section id="primary" class="content-area">
		<main id="main" class="site-main">

		<?php

		/* Start the Loop */
		while ( have_posts() ) :
        the_post(); ?>
 
        <div style="width: 70%; padding: 50px;"><h4><?php the_title(); ?></h4>
 
        <span style="color: blue;">ID=<?php the_ID(); ?></span>
        <span style="color: green;">
        <?php 
        #the_meta(); 
        if ( $keys = get_post_custom_keys() ) 
            {
            echo "<ul class='post-meta'>\n";
            foreach ( (array) $keys as $key ) 
                {
                $keyt = trim( $key );
                if ( is_protected_meta( $keyt, 'post' ) ) 
                    continue;
     
                $values = array_map( 'trim', get_post_custom_values( $key ) );
                $value = implode( $values, ', ' );
     
                if ($key === 'link')
                    echo "link = <a href=\"$value\" target=\"_blank\">$value</a><br />";
                else
                    echo "$key = $value<br />";
                }
            }
?>
        </span>
        <?php the_content(); ?></div>
 
	<?php 

	endwhile; // End of the loop.
	?>

		</main><!-- #main -->
	</section><!-- #primary -->

<?php
#get_footer();
