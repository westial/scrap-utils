<?php

abstract class ClassABC {
    abstract public function execute();
}

class ClassA extends ClassABC{

    public function execute()
    {
        return 'Class A';
    }
}

class ClassB extends ClassABC{

    public function execute()
    {
        return 'Class B';
    }
}

class ContainerABC {

    public function __construct(
        ClassABC $class
    )
    {

    }
}