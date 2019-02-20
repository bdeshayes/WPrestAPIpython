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
##
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
##

				/*get_template_part( 'template-parts/content/content', 'single' );

				if ( is_singular( 'attachment' ) ) {
					// Parent post navigation.
					the_post_navigation(
						array(
							// translators: %s: parent post link 
							'prev_text' => sprintf( __( '<span class="meta-nav">Published in</span><span class="post-title">%s</span>', 'twentynineteen' ), '%title' ),
						)
					);
				} elseif ( is_singular( 'post' ) ) {
					// Previous/next post navigation.
					the_post_navigation(
						array(
							'next_text' => '<span class="meta-nav" aria-hidden="true">' . __( 'Next Post', 'twentynineteen' ) . '</span> ' .
								'<span class="screen-reader-text">' . __( 'Next post:', 'twentynineteen' ) . '</span> <br/>' .
								'<span class="post-title">%title</span>',
							'prev_text' => '<span class="meta-nav" aria-hidden="true">' . __( 'Previous Post', 'twentynineteen' ) . '</span> ' .
								'<span class="screen-reader-text">' . __( 'Previous post:', 'twentynineteen' ) . '</span> <br/>' .
								'<span class="post-title">%title</span>',
						)
					);
				}

				// If comments are open or we have at least one comment, load up the comment template.
				if ( comments_open() || get_comments_number() ) {
					comments_template();
				}*/

			endwhile; // End of the loop.
			?>

		</main><!-- #main -->
	</section><!-- #primary -->

<?php
#get_footer();
