package SomeHTML;
use strict;

my %autoclose; @autoclose{qw( basefont br area link img param hr input col frame isindex base meta)} = ();


sub new {
	my $class = shift @_;
	my %args = @_;
	my $self = {};
	bless $self;
	$self->{before} = [];
	$self->{after} = [];
	$self->{indent} = 0;
	if ($args{indent}) { $self->{indent} = $args{indent}; }

	if ($args{root}) { # i'm not the parent
		$self->{root} = $args{root}; 
	} else { # i am the parent
		if ($args{dtd}) {
			push @{$self->{before}}, 
					 [0, $args{dtd}];
		} else {
			push @{$self->{before}}, 
					 [0, qq(<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN")];
			push @{$self->{before}}, 
					 [0, qq(  "http://www.w3.org/TR/html4/loose.dtd">)]
		}
		$self->html();
	}

	return $self;
}

sub render {
	my ($self, @rest) = @_;
	my $render;
	my %args = @rest;
	my $path = $args{path};
	foreach my $level (qw(before after)) {
		foreach my $item ( @{$self->{$level}} ) {
			if (!ref($item)) {
				$render .= $item;
				$render .= "\n";
			} elsif (ref($item) eq 'ARRAY') {
				$render .= " " x $item->[0];
				$render .= $item->[1];
				$render .= "\n";
			} else {
				$render .= $item->render();
			}
		}
	}
	return $render;
}

sub close {
	my ($self, @rest) = @_;
	push @{$self->{before}}, shift @{$self->{after}};
	$self->{indent}--;
	return $self;
}

sub mark {
	my ($self) = @_;
	my $sub = SomeHTML->new(root => $self, indent => $self->{indent});
	push @{$self->{before}},  $sub;
	$self->close();
	return $sub;
}

sub indent {
	my ($self, $t) = @_;
	push @{$self->{before}}, [ $self->{indent}, $t];
	return $self;
}

sub text {
	my ($self, $t) = @_; 
	push @{$self->{before}}, [ $self->{indent}, $t];
	return $self;
}


# options are:
# ->func() # adds a <func> before the cursor and </func> after
# ->_func() # adds a <func/> before the cursor

sub AUTOLOAD {
	my ($self, @rest) = @_;
	my $called = lc $SomeHTML::AUTOLOAD;
	$called =~ s/SomeHTML:://i;
	my $close = 0; if ($called =~ /^_/) { $close = 1; $called =~ s/^_// } # ??
	if (exists $autoclose{lc($called)}) { $close = 1 };

	if (scalar @rest > 2) { die "called $called with too many arguments!" } # ??

	my $text;
	my $args;
	foreach my $f (@rest) {
		if (ref($f) eq '') { $text = $f; }
		if (ref($f) eq 'HASH') { $args = " ".join(" ", map { qq($_="$f->{$_}") } keys %$f ) }
	}

	if ($close && !$text) { # mutually exclusive
		push @{$self->{before}}, [ $self->{indent}, "<$called$args />"];
	} elsif (!$text) {
		push @{$self->{before}}, [ $self->{indent}, "<$called$args>"];
		unshift @{$self->{after}}, [ $self->{indent}++,"</$called>"];
	} elsif ($text) {
		push @{$self->{before}}, [ $self->{indent}, "<$called$args>$text</$called>" ];
	} 
	return $self;
}
1;
