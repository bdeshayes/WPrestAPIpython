<?php
/**
 * The template for displaying archive pages
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/
 *
 * @package WordPress
 * @subpackage Twenty_Nineteen
 * @since 1.0.0
 */

get_header();
?>

	<section id="primary" class="content-area">
		<main id="main" class="site-main">

		<?php if ( have_posts() ) : ?>

			<header class="page-header">
				<?php
					#the_archive_title( '<h1 class="page-title">', '</h1>' );
				?>
			</header><!-- .page-header -->

			<?php
			// Start the Loop.
			while ( have_posts() ) :
##
        the_post(); ?>
 
        <div style="width: 70%; padding: 50px;"><h4><?php the_title(); ?></h4>
 
        <span style="color: blue;">ID=<?php the_ID(); ?></span>
        <span style="color: green;">
<?php 
#the_meta(); # replaced the_meta() because I wanted to make the link active
        if ( $keys = get_post_custom_keys() ) 
            {
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
        <?php the_excerpt(); ?></div><hr>
 
    <?php 
##

				/*
				 * Include the Post-Format-specific template for the content.
				 * If you want to override this in a child theme, then include a file
				 * called content-___.php (where ___ is the Post Format name) and that will be used instead.
				 */
				#get_template_part( 'template-parts/content/content', 'excerpt' );

				// End the loop.
			endwhile;

			// Previous/next page navigation.
			#twentynineteen_the_posts_navigation();

			// If no content, include the "No posts found" template.
		else :
			#get_template_part( 'template-parts/content/content', 'none' );

		endif;
		?>
		</main><!-- #main -->
	</section><!-- #primary -->

<?php
#get_footer();
