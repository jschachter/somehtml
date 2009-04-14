#!/usr/bin/perl

use SomeHTML;

my $h = new SomeHTML;


$head = $h->head()->mark();
$body = $h->body()->mark();

$head->title('hello');
$head->_meta( {foo => 'bar', bla => 'baz'});
$head->_meta( {foqewqwe => 'bar', bla => 'baz'});

$body->table({ class => 'bacon', id => 'slornt'});
for my $i ( 1 .. 4 ) {
	$body->tr();
	for my $j (5 .. 8 ) {
		$body->td("$i $j");
	}
	$body->close();
}
$body->close();
$body->hr();

print $h->render;

